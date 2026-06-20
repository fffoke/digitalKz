import api from '@/axios/axios'

export const getMyProfile = () => api.get('/me/profile')

export const updateProfile = (data) => api.patch('/profile', data)

export const getUserProfile = (username) => api.get(`/users/${username}`)

export const uploadAvatar = (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/profile/avatar', fd)
}
