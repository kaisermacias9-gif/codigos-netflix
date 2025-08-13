# StreamManager Pro - Contratos API y Backend Integration

## 📋 Datos Mockeados a Reemplazar

### Frontend Mock Data (`/app/frontend/src/data/mock.js`):
- `subscribers[]` - Lista completa de suscriptores
- `streamingServices[]` - Lista de servicios disponibles
- Funciones `getServiceColor()` y `getStatusColor()` se mantienen en frontend

## 🔌 Contratos de API

### 1. GET /api/subscribers
**Propósito**: Obtener todos los suscriptores
**Response**: 
```json
{
  "subscribers": [
    {
      "id": "string",
      "service": "string",
      "name": "string", 
      "phone": "string",
      "email": "string",
      "expirationDate": "YYYY-MM-DD",
      "daysRemaining": number,
      "status": "active|expiring|expired",
      "createdAt": "ISO string",
      "updatedAt": "ISO string"
    }
  ]
}
```

### 2. POST /api/subscribers
**Propósito**: Crear nuevo suscriptor
**Request Body**:
```json
{
  "service": "string",
  "name": "string",
  "phone": "string", 
  "email": "string",
  "expirationDate": "YYYY-MM-DD"
}
```
**Response**: Suscriptor creado

### 3. PUT /api/subscribers/{id}
**Propósito**: Actualizar suscriptor
**Request Body**: Campos a actualizar
**Response**: Suscriptor actualizado

### 4. DELETE /api/subscribers/{id}  
**Propósito**: Eliminar suscriptor
**Response**: Confirmación

### 5. GET /api/stats
**Propósito**: Obtener estadísticas del dashboard
**Response**:
```json
{
  "total": number,
  "expiring": number,
  "active": number,
  "expired": number,
  "revenue": number
}
```

### 6. POST /api/send-message
**Propósito**: Enviar mensaje/recordatorio
**Request Body**:
```json
{
  "subscriberId": "string",
  "messageType": "recordatorio|vencimiento|personalizado",
  "message": "string (opcional para tipos predefinidos)"
}
```
**Response**: Confirmación de envío

### 7. GET /api/services
**Propósito**: Obtener lista de servicios disponibles
**Response**:
```json
{
  "services": ["NETFLIX", "AMAZON PRIME", "DISNEY+", ...]
}
```

## 🗄️ Modelos de Base de Datos

### Subscriber Model
```javascript
{
  _id: ObjectId,
  service: String (required),
  name: String (required),
  phone: String (required),
  email: String (required),
  expirationDate: Date (required),
  status: String (enum: active, expiring, expired),
  createdAt: Date (default: now),
  updatedAt: Date (default: now)
}
```

### MessageLog Model (para auditoría)
```javascript
{
  _id: ObjectId,
  subscriberId: ObjectId (ref: Subscriber),
  messageType: String,
  message: String,
  sentAt: Date (default: now),
  status: String (enum: sent, failed)
}
```

## 🔄 Integración Frontend-Backend

### Cambios en Frontend:
1. Crear `api.js` para manejar todas las llamadas HTTP
2. Reemplazar mock data con llamadas reales en `Dashboard.jsx`
3. Agregar estados de loading y error handling
4. Implementar formulario para agregar nuevos suscriptores
5. Conectar botones de mensajes con API real

### Funcionalidades Backend:
1. CRUD completo de suscriptores
2. Cálculo automático de días restantes y status
3. Endpoint de estadísticas
4. Sistema de mensajería (mock inicial, puede expandirse a WhatsApp/SMS)
5. Validaciones de datos
6. Manejo de errores

### Flujo de Integración:
1. **Dashboard cargar**: GET /api/subscribers + GET /api/stats
2. **Filtros aplicar**: Frontend filtra localmente (performance)
3. **Nuevo suscriptor**: POST /api/subscribers → refresh data
4. **Enviar mensaje**: POST /api/send-message → mostrar toast
5. **Editar/Eliminar**: PUT/DELETE /api/subscribers/{id} → refresh data

## 📱 Sistema de Mensajería (Fase 1)
- Mensajes simulados (console.log + toast notification)
- Base para integración futura con WhatsApp Business API o SMS
- Log de mensajes enviados en base de datos

## 🎯 Prioridades de Implementación:
1. Modelos de base de datos
2. CRUD endpoints de suscriptores
3. Endpoint de estadísticas
4. Sistema de mensajería básico
5. Integración frontend completa
6. Testing y refinamiento