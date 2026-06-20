import api from '@/axios/axios'

export const queueDuel = () => api.post('/duels/queue')

export const getDuel = (id) => api.get(`/duels/${id}`)

export const answerDuel = (id, text) => api.post(`/duels/${id}/answer`, { text })

export const getLeaderboard = () => api.get('/duels/leaderboard')

export const getMyDuels = () => api.get('/duels')
