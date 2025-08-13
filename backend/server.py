from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from typing import List

from models import (
    Subscriber, SubscriberCreate, SubscriberUpdate, 
    MessageLogCreate, StatsResponse, SubscribersResponse, 
    ServicesResponse, MessageResponse, ServiceType, MessageType
)
from database import db

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="StreamManager Pro API", version="1.0.0")

# Create API router
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_database():
    return db

# Startup event
@app.on_event("startup")
async def startup_event():
    await db.connect()
    logger.info("StreamManager Pro API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await db.disconnect()
    logger.info("StreamManager Pro API stopped")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "StreamManager Pro API is running", "version": "1.0.0"}

# Get all subscribers
@api_router.get("/subscribers", response_model=SubscribersResponse)
async def get_subscribers(database = Depends(get_database)):
    try:
        subscribers = await database.get_subscribers()
        return SubscribersResponse(
            subscribers=subscribers,
            total=len(subscribers)
        )
    except Exception as e:
        logger.error(f"Error getting subscribers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Create new subscriber
@api_router.post("/subscribers", response_model=Subscriber)
async def create_subscriber(
    subscriber_data: SubscriberCreate, 
    database = Depends(get_database)
):
    try:
        subscriber = await database.create_subscriber(subscriber_data)
        return subscriber
    except Exception as e:
        logger.error(f"Error creating subscriber: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscriber")

# Get subscriber by ID
@api_router.get("/subscribers/{subscriber_id}", response_model=Subscriber)
async def get_subscriber(
    subscriber_id: str, 
    database = Depends(get_database)
):
    try:
        subscriber = await database.get_subscriber_by_id(subscriber_id)
        if not subscriber:
            raise HTTPException(status_code=404, detail="Subscriber not found")
        return subscriber
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscriber {subscriber_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Update subscriber
@api_router.put("/subscribers/{subscriber_id}", response_model=Subscriber)
async def update_subscriber(
    subscriber_id: str,
    update_data: SubscriberUpdate,
    database = Depends(get_database)
):
    try:
        subscriber = await database.update_subscriber(subscriber_id, update_data)
        if not subscriber:
            raise HTTPException(status_code=404, detail="Subscriber not found")
        return subscriber
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscriber {subscriber_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update subscriber")

# Delete subscriber
@api_router.delete("/subscribers/{subscriber_id}")
async def delete_subscriber(
    subscriber_id: str,
    database = Depends(get_database)
):
    try:
        deleted = await database.delete_subscriber(subscriber_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Subscriber not found")
        return {"message": "Subscriber deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting subscriber {subscriber_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete subscriber")

# Get dashboard statistics
@api_router.get("/stats", response_model=StatsResponse)
async def get_stats(database = Depends(get_database)):
    try:
        stats = await database.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Send message to subscriber
@api_router.post("/send-message", response_model=MessageResponse)
async def send_message(
    message_data: MessageLogCreate,
    database = Depends(get_database)
):
    try:
        # Get subscriber info
        subscriber = await database.get_subscriber_by_id(message_data.subscriberId)
        if not subscriber:
            raise HTTPException(status_code=404, detail="Subscriber not found")
        
        # Generate message content based on type
        if message_data.messageType == MessageType.RECORDATORIO:
            message_content = f"Hola {subscriber.name}, te recordamos que tu suscripción a {subscriber.service} vence el {subscriber.expirationDate}. ¡Renuévala para seguir disfrutando!"
        elif message_data.messageType == MessageType.VENCIMIENTO:
            message_content = f"¡Atención {subscriber.name}! Tu suscripción a {subscriber.service} vence en {subscriber.daysRemaining} días ({subscriber.expirationDate}). Renueva ahora para no perder acceso."
        else:
            message_content = message_data.message or "Mensaje personalizado enviado."
        
        # Create message log
        message_log_data = MessageLogCreate(
            subscriberId=message_data.subscriberId,
            messageType=message_data.messageType,
            message=message_content
        )
        
        message_log = await database.create_message_log(message_log_data)
        
        # Simulate sending message (in real implementation, integrate with WhatsApp/SMS API)
        logger.info(f"Message sent to {subscriber.name} ({subscriber.phone}): {message_content}")
        
        return MessageResponse(
            success=True,
            message=f"Mensaje enviado exitosamente a {subscriber.name}",
            messageLog=message_log
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

# Get available streaming services
@api_router.get("/services", response_model=ServicesResponse)
async def get_services():
    try:
        services = [service.value for service in ServiceType]
        return ServicesResponse(services=services)
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include router in app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)