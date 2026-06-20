import api from '@/axios/axios'

// filter: all | follows | mentions
export const getNotifications = (filter = 'all') =>
    api.get('/notifications', { params: { filter } })
