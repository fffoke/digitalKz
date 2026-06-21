import api from '@/axios/axios'

export const getLearningOverview = () => api.get('/learning/overview')
export const getEntranceExam = () => api.get('/learning/entrance/exam')
export const submitEntranceTest = (data) => api.post('/learning/entrance/submit', data)
export const getLevelExam = () => api.get('/learning/level-exam')
export const submitLevelExam = (answers, audioBlob) => {
  const fd = new FormData()
  fd.append('answers', JSON.stringify(answers || {}))
  if (audioBlob) fd.append('audio', audioBlob, 'speak.webm')
  return api.post('/learning/level-exam/submit', fd)
}
export const startLesson = (groupId) => api.post(`/learning/teacher/groups/${groupId}/start-lesson`)
export const createGroup = (data) => api.post('/learning/groups', data)
export const joinGroup = (id) => api.post(`/learning/groups/${id}/join`)
export const joinGroupByCode = (invite_code) => api.post('/learning/groups/join-by-code', { invite_code })
export const leaveGroup = (groupId) => api.post(`/learning/groups/${groupId}/leave`)
export const getGroupMessages = (groupId) => api.get(`/learning/groups/${groupId}/messages`)
export const sendGroupMessage = (groupId, text) => api.post(`/learning/groups/${groupId}/messages`, { text })
export const scheduleLesson = (groupId, starts_at) => api.post(`/learning/teacher/groups/${groupId}/lessons`, { starts_at })
export const completeLesson = (lessonId) => api.post(`/learning/teacher/lessons/${lessonId}/complete`)
export const getHomeworks = () => api.get('/learning/homeworks')
export const submitHomework = (homeworkId, submission, file) => {
  const fd = new FormData()
  fd.append('submission', submission || '')
  if (file) fd.append('file', file)
  return api.post(`/learning/homeworks/${homeworkId}/submit`, fd)
}
export const gradeHomework = (homeworkId, data) => api.post(`/learning/teacher/homeworks/${homeworkId}/grade`, data)
export const rateLesson = (lessonId, data) => api.post(`/learning/lessons/${lessonId}/rate`, data)
