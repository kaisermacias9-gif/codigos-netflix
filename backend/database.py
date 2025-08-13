from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date
import os
from typing import List, Optional
from models import Subscriber, SubscriberCreate, SubscriberUpdate, MessageLog, MessageLogCreate, SubscriberStatus
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongo_url = os.environ['MONGO_URL']
            db_name = os.environ.get('DB_NAME', 'streammanager')
            
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ismaster')
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    def calculate_days_remaining(self, expiration_date: date) -> int:
        """Calculate days remaining until expiration"""
        today = date.today()
        delta = expiration_date - today
        return delta.days

    def calculate_status(self, days_remaining: int) -> SubscriberStatus:
        """Calculate subscriber status based on days remaining"""
        if days_remaining < 0:
            return SubscriberStatus.EXPIRED
        elif days_remaining <= 7:
            return SubscriberStatus.EXPIRING
        else:
            return SubscriberStatus.ACTIVE

    async def create_subscriber(self, subscriber_data: SubscriberCreate) -> Subscriber:
        """Create a new subscriber"""
        try:
            # Calculate derived fields
            days_remaining = self.calculate_days_remaining(subscriber_data.expirationDate)
            status = self.calculate_status(days_remaining)
            
            # Create subscriber object
            subscriber = Subscriber(
                **subscriber_data.dict(),
                status=status,
                daysRemaining=days_remaining
            )
            
            # Insert into database - convert date objects to strings for MongoDB
            subscriber_dict = subscriber.dict()
            if 'expirationDate' in subscriber_dict:
                subscriber_dict['expirationDate'] = subscriber_dict['expirationDate'].isoformat()
            if 'createdAt' in subscriber_dict:
                subscriber_dict['createdAt'] = subscriber_dict['createdAt'].isoformat()
            if 'updatedAt' in subscriber_dict:
                subscriber_dict['updatedAt'] = subscriber_dict['updatedAt'].isoformat()
            
            result = await self.db.subscribers.insert_one(subscriber_dict)
            
            if result.inserted_id:
                logger.info(f"Created subscriber: {subscriber.name}")
                return subscriber
            else:
                raise Exception("Failed to insert subscriber")
                
        except Exception as e:
            logger.error(f"Error creating subscriber: {e}")
            raise

    async def get_subscribers(self) -> List[Subscriber]:
        """Get all subscribers with updated status and days remaining"""
        try:
            cursor = self.db.subscribers.find()
            subscribers = []
            
            async for doc in cursor:
                # Recalculate status and days remaining
                days_remaining = self.calculate_days_remaining(doc['expirationDate'])
                status = self.calculate_status(days_remaining)
                
                # Update document with current values
                doc['daysRemaining'] = days_remaining
                doc['status'] = status
                doc['updatedAt'] = datetime.utcnow()
                
                # Update in database if values changed
                await self.db.subscribers.update_one(
                    {'_id': doc['_id']},
                    {'$set': {
                        'daysRemaining': days_remaining,
                        'status': status,
                        'updatedAt': datetime.utcnow()
                    }}
                )
                
                subscribers.append(Subscriber(**doc))
            
            logger.info(f"Retrieved {len(subscribers)} subscribers")
            return subscribers
            
        except Exception as e:
            logger.error(f"Error getting subscribers: {e}")
            raise

    async def get_subscriber_by_id(self, subscriber_id: str) -> Optional[Subscriber]:
        """Get a subscriber by ID"""
        try:
            doc = await self.db.subscribers.find_one({'id': subscriber_id})
            
            if doc:
                # Recalculate status and days remaining
                days_remaining = self.calculate_days_remaining(doc['expirationDate'])
                status = self.calculate_status(days_remaining)
                
                doc['daysRemaining'] = days_remaining
                doc['status'] = status
                
                return Subscriber(**doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting subscriber {subscriber_id}: {e}")
            raise

    async def update_subscriber(self, subscriber_id: str, update_data: SubscriberUpdate) -> Optional[Subscriber]:
        """Update a subscriber"""
        try:
            # Get current subscriber
            current = await self.get_subscriber_by_id(subscriber_id)
            if not current:
                return None
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict['updatedAt'] = datetime.utcnow()
            
            # If expiration date is being updated, recalculate status
            if 'expirationDate' in update_dict:
                days_remaining = self.calculate_days_remaining(update_dict['expirationDate'])
                status = self.calculate_status(days_remaining)
                update_dict['daysRemaining'] = days_remaining
                update_dict['status'] = status
            
            # Update in database
            result = await self.db.subscribers.update_one(
                {'id': subscriber_id},
                {'$set': update_dict}
            )
            
            if result.modified_count > 0:
                updated_subscriber = await self.get_subscriber_by_id(subscriber_id)
                logger.info(f"Updated subscriber: {subscriber_id}")
                return updated_subscriber
            
            return current
            
        except Exception as e:
            logger.error(f"Error updating subscriber {subscriber_id}: {e}")
            raise

    async def delete_subscriber(self, subscriber_id: str) -> bool:
        """Delete a subscriber"""
        try:
            result = await self.db.subscribers.delete_one({'id': subscriber_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted subscriber: {subscriber_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting subscriber {subscriber_id}: {e}")
            raise

    async def get_stats(self) -> dict:
        """Get dashboard statistics"""
        try:
            subscribers = await self.get_subscribers()
            
            total = len(subscribers)
            expiring = len([s for s in subscribers if s.status == SubscriberStatus.EXPIRING])
            active = len([s for s in subscribers if s.status == SubscriberStatus.ACTIVE])
            expired = len([s for s in subscribers if s.status == SubscriberStatus.EXPIRED])
            
            # Calculate revenue (assuming $15 per active subscription)
            revenue = (active + expiring) * 15.0
            
            return {
                'total': total,
                'expiring': expiring,
                'active': active,
                'expired': expired,
                'revenue': revenue
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise

    async def create_message_log(self, message_data: MessageLogCreate) -> MessageLog:
        """Create a message log entry"""
        try:
            message_log = MessageLog(
                **message_data.dict(),
                status="sent"  # For now, assume all messages are sent successfully
            )
            
            result = await self.db.message_logs.insert_one(message_log.dict())
            
            if result.inserted_id:
                logger.info(f"Created message log for subscriber: {message_data.subscriberId}")
                return message_log
            else:
                raise Exception("Failed to insert message log")
                
        except Exception as e:
            logger.error(f"Error creating message log: {e}")
            raise

# Global database instance
db = Database()