import React, { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { 
  Search, 
  Plus, 
  MessageCircle, 
  Calendar, 
  Users, 
  TrendingUp,
  Mail,
  Phone,
  Loader2,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { subscribersApi, statsApi, messagesApi, servicesApi } from '../api/api';
import { getServiceColor, getStatusColor } from '../data/mock';
import { useToast } from '../hooks/use-toast';
import AddSubscriberModal from './AddSubscriberModal';

const Dashboard = () => {
  // State management
  const [subscribers, setSubscribers] = useState([]);
  const [stats, setStats] = useState({ total: 0, expiring: 0, active: 0, revenue: 0 });
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sendingMessage, setSendingMessage] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterService, setFilterService] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  const { toast } = useToast();

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [subscribersResponse, statsResponse, servicesResponse] = await Promise.all([
        subscribersApi.getAll(),
        statsApi.get(),
        servicesApi.getAll()
      ]);
      
      setSubscribers(subscribersResponse.subscribers || []);
      setStats(statsResponse);
      setServices(servicesResponse.services || []);
      
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Error al cargar los datos. Por favor, intenta de nuevo.');
      toast({
        title: "Error",
        description: "Error al cargar los datos. Por favor, intenta de nuevo.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      setRefreshing(true);
      await loadInitialData();
      toast({
        title: "Éxito",
        description: "Datos actualizados correctamente.",
        variant: "default"
      });
    } catch (err) {
      toast({
        title: "Error",
        description: "Error al actualizar los datos.",
        variant: "destructive"
      });
    } finally {
      setRefreshing(false);
    }
  };

  // Filter subscribers
  const filteredSubscribers = useMemo(() => {
    return subscribers.filter(sub => {
      const matchesSearch = sub.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           sub.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           sub.phone.includes(searchTerm);
      
      const matchesService = filterService === 'all' || sub.service === filterService;
      
      const matchesStatus = filterStatus === 'all' || 
                           (filterStatus === 'expiring' && sub.daysRemaining <= 7) ||
                           (filterStatus === 'active' && sub.daysRemaining > 7);
      
      return matchesSearch && matchesService && matchesStatus;
    });
  }, [subscribers, searchTerm, filterService, filterStatus]);

  // Send message handler
  const handleSendMessage = async (subscriber, messageType) => {
    try {
      setSendingMessage(`${subscriber.id}-${messageType}`);
      
      const messageData = {
        subscriberId: subscriber.id,
        messageType: messageType
      };
      
      const response = await messagesApi.send(messageData);
      
      toast({
        title: "Mensaje enviado",
        description: response.message,
        variant: "default"
      });
      
    } catch (err) {
      console.error('Error sending message:', err);
      toast({
        title: "Error",
        description: "Error al enviar el mensaje. Por favor, intenta de nuevo.",
        variant: "destructive"
      });
    } finally {
      setSendingMessage(null);
    }
  };

  // Add subscriber handler
  const handleAddSubscriber = async (subscriberData) => {
    try {
      await subscribersApi.create(subscriberData);
      
      toast({
        title: "Éxito",
        description: "Suscriptor agregado correctamente.",
        variant: "default"
      });
      
      // Refresh data
      await loadInitialData();
      setIsModalOpen(false);
      
    } catch (err) {
      console.error('Error creating subscriber:', err);
      toast({
        title: "Error",
        description: "Error al agregar el suscriptor. Por favor, verifica los datos.",
        variant: "destructive"
      });
      throw err; // Re-throw to handle in modal
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
          <p className="text-slate-600">Cargando datos...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4 text-center">
          <AlertCircle className="h-8 w-8 text-red-600" />
          <p className="text-slate-600">{error}</p>
          <Button onClick={loadInitialData} className="bg-emerald-600 hover:bg-emerald-700">
            Reintentar
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
              StreamManager Pro
            </h1>
            <p className="text-slate-600 mt-1">Gestiona tus suscriptores de streaming</p>
          </div>
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              onClick={refreshData}
              disabled={refreshing}
              className="border-slate-300"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
            <Button 
              onClick={() => setIsModalOpen(true)}
              className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 shadow-lg"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Suscriptor
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-blue-700">Total Suscriptores</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-900">{stats.total}</div>
              <p className="text-xs text-blue-600 mt-1">Usuarios registrados</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-orange-700">Por Vencer</CardTitle>
              <Calendar className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-900">{stats.expiring}</div>
              <p className="text-xs text-orange-600 mt-1">Próximos 7 días</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-green-700">Activos</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-900">{stats.active}</div>
              <p className="text-xs text-green-600 mt-1">Suscripciones vigentes</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-gradient-to-br from-emerald-50 to-emerald-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-emerald-700">Ingresos</CardTitle>
              <TrendingUp className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-900">${stats.revenue}</div>
              <p className="text-xs text-emerald-600 mt-1">Ingresos mensuales</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Buscar por nombre, email o teléfono..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 border-slate-200 focus:border-emerald-500 focus:ring-emerald-500"
                />
              </div>
              
              <div className="flex gap-3">
                <select
                  value={filterService}
                  onChange={(e) => setFilterService(e.target.value)}
                  className="px-4 py-2 border border-slate-200 rounded-md focus:border-emerald-500 focus:ring-emerald-500"
                >
                  <option value="all">Todos los servicios</option>
                  {services.map(service => (
                    <option key={service} value={service}>{service}</option>
                  ))}
                </select>

                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-slate-200 rounded-md focus:border-emerald-500 focus:ring-emerald-500"
                >
                  <option value="all">Todos los estados</option>
                  <option value="active">Activos</option>
                  <option value="expiring">Por vencer</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Subscribers Table */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl text-slate-800">
              Suscriptores ({filteredSubscribers.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="text-left p-4 font-semibold text-slate-700">Servicio</th>
                    <th className="text-left p-4 font-semibold text-slate-700">Nombre</th>
                    <th className="text-left p-4 font-semibold text-slate-700">Contacto</th>
                    <th className="text-left p-4 font-semibold text-slate-700">Vencimiento</th>
                    <th className="text-left p-4 font-semibold text-slate-700">Días Restantes</th>
                    <th className="text-left p-4 font-semibold text-slate-700">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSubscribers.map((subscriber, index) => (
                    <tr key={subscriber.id} className={`border-b border-slate-100 hover:bg-slate-50 transition-colors ${index % 2 === 0 ? 'bg-white' : 'bg-slate-25'}`}>
                      <td className="p-4">
                        <Badge className={`${getServiceColor(subscriber.service)} text-white font-medium`}>
                          {subscriber.service}
                        </Badge>
                      </td>
                      <td className="p-4 font-medium text-slate-900">{subscriber.name}</td>
                      <td className="p-4">
                        <div className="space-y-1">
                          <div className="flex items-center text-sm text-slate-600">
                            <Mail className="w-3 h-3 mr-2" />
                            {subscriber.email}
                          </div>
                          <div className="flex items-center text-sm text-slate-600">
                            <Phone className="w-3 h-3 mr-2" />
                            {subscriber.phone}
                          </div>
                        </div>
                      </td>
                      <td className="p-4 text-slate-700">{subscriber.expirationDate}</td>
                      <td className="p-4">
                        <Badge className={`${getStatusColor(subscriber.daysRemaining)} font-medium`}>
                          {subscriber.daysRemaining} días
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSendMessage(subscriber, 'recordatorio')}
                            disabled={sendingMessage === `${subscriber.id}-recordatorio`}
                            className="border-blue-200 text-blue-700 hover:bg-blue-50"
                          >
                            {sendingMessage === `${subscriber.id}-recordatorio` ? (
                              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                            ) : (
                              <MessageCircle className="w-3 h-3 mr-1" />
                            )}
                            Recordatorio
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSendMessage(subscriber, 'vencimiento')}
                            disabled={sendingMessage === `${subscriber.id}-vencimiento`}
                            className="border-orange-200 text-orange-700 hover:bg-orange-50"
                          >
                            {sendingMessage === `${subscriber.id}-vencimiento` ? (
                              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                            ) : (
                              <Calendar className="w-3 h-3 mr-1" />
                            )}
                            Vencimiento
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {filteredSubscribers.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                No se encontraron suscriptores que coincidan con los filtros.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Add Subscriber Modal */}
      <AddSubscriberModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddSubscriber}
        services={services}
      />
    </div>
  );
};

export default Dashboard;