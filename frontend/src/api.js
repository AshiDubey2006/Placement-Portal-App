import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

// Attach JWT on every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Global 401 handler — redirect to login
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userRole')
      localStorage.removeItem('userName')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  auth: {
    login: (credentials) => api.post('/auth/login', credentials),
    register: (userData) => api.post('/auth/register', userData),
    getCurrentUser: () => api.get('/auth/me'),
    changePassword: (data) => api.post('/auth/change-password', data)
  },

  admin: {
    getDashboard: () => api.get('/admin/dashboard'),
    getCompanies: (params) => api.get('/admin/companies', { params }),
    approveCompany: (id) => api.post(`/admin/companies/${id}/approve`),
    rejectCompany: (id) => api.post(`/admin/companies/${id}/reject`),
    blacklistCompany: (id) => api.post(`/admin/companies/${id}/blacklist`),
    activateCompany: (id) => api.post(`/admin/companies/${id}/activate`),
    getStudents: (params) => api.get('/admin/students', { params }),
    blacklistStudent: (id) => api.post(`/admin/students/${id}/blacklist`),
    activateStudent: (id) => api.post(`/admin/students/${id}/activate`),
    getDrives: (params) => api.get('/admin/drives', { params }),
    approveDrive: (id) => api.post(`/admin/drives/${id}/approve`),
    rejectDrive: (id) => api.post(`/admin/drives/${id}/reject`),
    getApplications: (params) => api.get('/admin/applications', { params }),
    getStatistics: () => api.get('/admin/statistics')
  },

  company: {
    getProfile: () => api.get('/company/profile'),
    updateProfile: (data) => api.put('/company/profile', data),
    getDashboard: () => api.get('/company/dashboard'),
    createDrive: (data) => api.post('/company/drives', data),
    getDrives: () => api.get('/company/drives'),
    updateDrive: (id, data) => api.put(`/company/drives/${id}`, data),
    closeDrive: (id) => api.put(`/company/drives/${id}/close`),
    deleteDrive: (id) => api.delete(`/company/drives/${id}`),
    getDriveApplications: (id) => api.get(`/company/drives/${id}/applications`),
    shortlistStudent: (id, data) => api.post(`/company/applications/${id}/shortlist`, data),
    selectStudent: (id) => api.post(`/company/applications/${id}/select`),
    rejectStudent: (id, data) => api.post(`/company/applications/${id}/reject`, data),
    generateOfferLetter: (id) => api.get(`/company/applications/${id}/offer-letter`, {
      responseType: 'blob'
    })
  },

  student: {
    getProfile: () => api.get('/student/profile'),
    updateProfile: (data) => api.put('/student/profile', data),
    uploadResume: (formData) => api.post('/student/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    getDashboard: () => api.get('/student/dashboard'),
    getApplications: () => api.get('/student/applications'),
    exportApplications: () => api.post('/student/applications/export'),
    getExportStatus: (taskId) => api.get(`/student/applications/export/status/${taskId}`),
    downloadExport: (filename) => api.get(`/student/applications/download/${filename}`, {
      responseType: 'blob'
    })
  },

  drive: {
    getAll: (params) => api.get('/drive/', { params }),
    getById: (id) => api.get(`/drive/${id}`),
    apply: (id) => api.post(`/drive/${id}/apply`),
    search: (params) => api.get('/drive/search', { params })
  }
}
