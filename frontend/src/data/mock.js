export const streamingServices = [
  'NETFLIX',
  'AMAZON PRIME',
  'DISNEY+',
  'HBO MAX',
  'SPOTIFY',
  'YOUTUBE PREMIUM',
  'APPLE TV+',
  'PARAMOUNT+'
];

export const subscribers = [
  {
    id: '1',
    service: 'NETFLIX',
    name: 'AKIRO',
    phone: '963755815',
    email: 'akiro60@gmail.com',
    expirationDate: '2025-08-23',
    daysRemaining: 10,
    status: 'active'
  },
  {
    id: '2',
    service: 'NETFLIX',
    name: 'NANCY',
    phone: '978988799',
    email: 'nancy60@gmail.com',
    expirationDate: '2025-08-21',
    daysRemaining: 8,
    status: 'active'
  },
  {
    id: '3',
    service: 'NETFLIX',
    name: 'MARIELA',
    phone: '985500286',
    email: 'mariela60@gmail.com',
    expirationDate: '2025-08-31',
    daysRemaining: 18,
    status: 'active'
  },
  {
    id: '4',
    service: 'NETFLIX',
    name: 'ADRIEL',
    phone: '986805376',
    email: 'adriel60@gmail.com',
    expirationDate: '2025-09-08',
    daysRemaining: 26,
    status: 'active'
  },
  {
    id: '5',
    service: 'NETFLIX',
    name: 'EDISON',
    phone: '979679208',
    email: 'edison125@gmail.com',
    expirationDate: '2025-08-14',
    daysRemaining: 1,
    status: 'expiring'
  },
  {
    id: '6',
    service: 'NETFLIX',
    name: 'NORMA',
    phone: '993188266',
    email: 'norma125@gmail.com',
    expirationDate: '2025-09-04',
    daysRemaining: 22,
    status: 'active'
  },
  {
    id: '7',
    service: 'AMAZON PRIME',
    name: 'JENETH',
    phone: '980002981',
    email: 'jeneth125@gmail.com',
    expirationDate: '2025-08-20',
    daysRemaining: 7,
    status: 'active'
  },
  {
    id: '8',
    service: 'DISNEY+',
    name: 'PRISCILA',
    phone: '962747671',
    email: 'priscila125@gmail.com',
    expirationDate: '2025-08-18',
    daysRemaining: 5,
    status: 'expiring'
  },
  {
    id: '9',
    service: 'HBO MAX',
    name: 'CANDY',
    phone: '984936373',
    email: 'candy34@gmail.com',
    expirationDate: '2025-08-14',
    daysRemaining: 1,
    status: 'expiring'
  },
  {
    id: '10',
    service: 'SPOTIFY',
    name: 'JORGE',
    phone: '984936373',
    email: 'jorge34@gmail.com',
    expirationDate: '2025-09-02',
    daysRemaining: 20,
    status: 'active'
  }
];

export const getServiceColor = (service) => {
  const colors = {
    'NETFLIX': 'bg-red-500',
    'AMAZON PRIME': 'bg-blue-600',
    'DISNEY+': 'bg-indigo-600',
    'HBO MAX': 'bg-purple-600',
    'SPOTIFY': 'bg-green-500',
    'YOUTUBE PREMIUM': 'bg-red-600',
    'APPLE TV+': 'bg-gray-800',
    'PARAMOUNT+': 'bg-blue-700'
  };
  return colors[service] || 'bg-gray-500';
};

export const getStatusColor = (daysRemaining) => {
  if (daysRemaining <= 3) return 'text-red-600 bg-red-50';
  if (daysRemaining <= 7) return 'text-orange-600 bg-orange-50';
  return 'text-green-600 bg-green-50';
};