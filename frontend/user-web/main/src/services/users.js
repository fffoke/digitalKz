import api from '@/axios/axios'

export const getMyProfile = () => api.get('/me/profile')

export const updateProfile = (data) => api.patch('/profile', data)

export const getUserProfile = (username) => api.get(`/users/${username}`)
