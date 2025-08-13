import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { X, Loader2, User, Mail, Phone, Calendar, Monitor } from 'lucide-react';

const AddSubscriberModal = ({ isOpen, onClose, onSubmit, services = [] }) => {
  const [formData, setFormData] = useState({
    service: '',
    name: '',
    phone: '',
    email: '',
    expirationDate: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.service) newErrors.service = 'Selecciona un servicio';
    if (!formData.name.trim()) newErrors.name = 'Ingresa el nombre';
    if (!formData.phone.trim()) newErrors.phone = 'Ingresa el teléfono';
    if (!formData.email.trim()) newErrors.email = 'Ingresa el email';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email inválido';
    if (!formData.expirationDate) newErrors.expirationDate = 'Selecciona la fecha de vencimiento';
    else {
      const selectedDate = new Date(formData.expirationDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (selectedDate < today) newErrors.expirationDate = 'La fecha debe ser futura';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      setLoading(true);
      await onSubmit(formData);
      
      // Reset form
      setFormData({
        service: '',
        name: '',
        phone: '',
        email: '',
        expirationDate: ''
      });
      setErrors({});
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        service: '',
        name: '',
        phone: '',
        email: '',
        expirationDate: ''
      });
      setErrors({});
      onClose();
    }
  };

  // Get minimum date (today)
  const today = new Date().toISOString().split('T')[0];

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px] p-0">
        <DialogHeader className="p-6 pb-4">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl font-semibold text-slate-800">
              Agregar Nuevo Suscriptor
            </DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              disabled={loading}
              className="h-8 w-8 p-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="px-6 pb-6 space-y-4">
          {/* Service Selection */}
          <div className="space-y-2">
            <Label htmlFor="service" className="text-sm font-medium text-slate-700 flex items-center">
              <Monitor className="w-4 h-4 mr-2" />
              Servicio de Streaming
            </Label>
            <select
              id="service"
              value={formData.service}
              onChange={(e) => handleChange('service', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 ${
                errors.service ? 'border-red-500' : 'border-slate-300'
              }`}
              disabled={loading}
            >
              <option value="">Selecciona un servicio</option>
              {services.map(service => (
                <option key={service} value={service}>{service}</option>
              ))}
            </select>
            {errors.service && (
              <p className="text-sm text-red-600">{errors.service}</p>
            )}
          </div>

          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium text-slate-700 flex items-center">
              <User className="w-4 h-4 mr-2" />
              Nombre Completo
            </Label>
            <Input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Ej: Juan Pérez"
              className={errors.name ? 'border-red-500' : ''}
              disabled={loading}
            />
            {errors.name && (
              <p className="text-sm text-red-600">{errors.name}</p>
            )}
          </div>

          {/* Phone */}
          <div className="space-y-2">
            <Label htmlFor="phone" className="text-sm font-medium text-slate-700 flex items-center">
              <Phone className="w-4 h-4 mr-2" />
              Teléfono
            </Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              placeholder="Ej: 987654321"
              className={errors.phone ? 'border-red-500' : ''}
              disabled={loading}
            />
            {errors.phone && (
              <p className="text-sm text-red-600">{errors.phone}</p>
            )}
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium text-slate-700 flex items-center">
              <Mail className="w-4 h-4 mr-2" />
              Email
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="Ej: juan@email.com"
              className={errors.email ? 'border-red-500' : ''}
              disabled={loading}
            />
            {errors.email && (
              <p className="text-sm text-red-600">{errors.email}</p>
            )}
          </div>

          {/* Expiration Date */}
          <div className="space-y-2">
            <Label htmlFor="expirationDate" className="text-sm font-medium text-slate-700 flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              Fecha de Vencimiento
            </Label>
            <Input
              id="expirationDate"
              type="date"
              value={formData.expirationDate}
              onChange={(e) => handleChange('expirationDate', e.target.value)}
              min={today}
              className={errors.expirationDate ? 'border-red-500' : ''}
              disabled={loading}
            />
            {errors.expirationDate && (
              <p className="text-sm text-red-600">{errors.expirationDate}</p>
            )}
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={loading}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Guardando...
                </>
              ) : (
                'Agregar Suscriptor'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddSubscriberModal;