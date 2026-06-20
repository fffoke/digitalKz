import api from '@/axios/axios'

export const getLearningOverview = () => api.get('/learning/overview')
export const submitEntranceTest = (data) => api.post('/learning/entrance/submit', data)
export const submitLevelExam = (data) => api.post('/learning/level-exam/submit', data)
export const createGroup = (data) => api.post('/learning/groups', data)
export const joinGroup = (id) => api.post(`/learning/groups/${id}/join`)
export const joinGroupByCode = (invite_code) => api.post('/learning/groups/join-by-code', { invite_code })
export const scheduleLesson = (groupId, starts_at) => api.post(`/learning/teacher/groups/${groupId}/lessons`, { starts_at })
export const completeLesson = (lessonId) => api.post(`/learning/teacher/lessons/${lessonId}/complete`)
export const submitHomework = (homeworkId, submission) => api.post(`/learning/homeworks/${homeworkId}/submit`, { submission })
export const gradeHomework = (homeworkId, data) => api.post(`/learning/teacher/homeworks/${homeworkId}/grade`, data)
export const rateLesson = (lessonId, data) => api.post(`/learning/lessons/${lessonId}/rate`, data)
