import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = {
  // 康复周期相关
  getCycles: () => axios.get(`${API_BASE_URL}/cycles`),
  getCycle: (id) => axios.get(`${API_BASE_URL}/cycles/${id}`),
  createCycle: (data) => axios.post(`${API_BASE_URL}/cycles`, data),
  updateCycle: (id, data) => axios.put(`${API_BASE_URL}/cycles/${id}`, data),
  deleteCycle: (id) => axios.delete(`${API_BASE_URL}/cycles/${id}`),
  
  // 训练任务相关
  getTasks: (params) => axios.get(`${API_BASE_URL}/tasks`, { params }),
  getTask: (id) => axios.get(`${API_BASE_URL}/tasks/${id}`),
  createTask: (data) => axios.post(`${API_BASE_URL}/tasks`, data),
  updateTask: (id, data) => axios.put(`${API_BASE_URL}/tasks/${id}`, data),
  completeTask: (id, data) => axios.post(`${API_BASE_URL}/tasks/${id}/complete`, data),
  
  // 运动类型相关
  getExercises: () => axios.get(`${API_BASE_URL}/exercises`),
  getExercise: (id) => axios.get(`${API_BASE_URL}/exercises/${id}`),
  createExercise: (data) => axios.post(`${API_BASE_URL}/exercises`, data),
  updateExercise: (id, data) => axios.put(`${API_BASE_URL}/exercises/${id}`, data),
  deleteExercise: (id) => axios.delete(`${API_BASE_URL}/exercises/${id}`),
  
  // 完成记录相关
  getCompletions: (params) => axios.get(`${API_BASE_URL}/completions`, { params }),
  getCompletion: (id) => axios.get(`${API_BASE_URL}/completions/${id}`),
  createCompletion: (data) => axios.post(`${API_BASE_URL}/completions`, data),
  updateCompletion: (id, data) => axios.put(`${API_BASE_URL}/completions/${id}`, data),
  deleteCompletion: (id) => axios.delete(`${API_BASE_URL}/completions/${id}`),
  getCompletionStats: (params) => axios.get(`${API_BASE_URL}/completions/stats`, { params }),
};

export default api;