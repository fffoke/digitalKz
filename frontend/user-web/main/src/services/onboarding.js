import api from '@/axios/axios'

// Старая идея — роли преподаватель/ученик, верификация. Вкладка «Обучение».
export const getRoleStatus = () => api.get('/me/role-status')

export const submitVerification = (iin, docFile) => {
    const fd = new FormData()
    fd.append('iin', iin)
    if (docFile) fd.append('doc_photo', docFile)
    return api.post('/verification', fd)
}

export const applyTeacher = (data) => api.post('/teacher/apply', data)
