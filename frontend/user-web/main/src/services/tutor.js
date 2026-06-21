import api from '@/axios/axios'

// --- онбординг интересов ---
export const getInterests = () => api.get('/me/interests')
export const saveInterests = (data) => api.post('/me/interests', data)

// --- статистика ученика ---
export const getStats = () => api.get('/me/stats')

// --- задания ---
export const generateTasks = () => api.post('/tasks/generate')
export const createCustomTask = (data) => api.post('/tasks/custom', data)
export const getTasks = () => api.get('/tasks')
export const getTask = (id) => api.get(`/tasks/${id}`)
export const deleteTask = (id) => api.delete(`/tasks/${id}`)
export const clearCompletedTasks = () => api.post('/tasks/clear-completed')

// --- сессия диалога ---
export const startTask = (taskId) => api.post(`/tasks/${taskId}/start`)
export const getSession = (sessionId) => api.get(`/sessions/${sessionId}`)
export const finishSession = (sessionId) => api.post(`/sessions/${sessionId}/finish`)

// голосовое сообщение — multipart (как загрузка аватара)
export const sendMessage = (sessionId, blob) => {
    const fd = new FormData()
    fd.append('audio', blob, 'voice.webm')
    return api.post(`/sessions/${sessionId}/message`, fd)
}
