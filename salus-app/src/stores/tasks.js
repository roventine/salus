import { defineStore } from 'pinia'
import api from '../api'

export const useTaskStore = defineStore('tasks', {
  state: () => ({
    tasks: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchTasks(params = {}) {
      this.loading = true
      try {
        const response = await api.getTasks(params)
        this.tasks = response.data
        this.error = null
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取训练任务失败'
        console.error('获取训练任务失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async getTask(id) {
      try {
        const response = await api.getTask(id)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取训练任务详情失败'
        console.error('获取训练任务详情失败:', error)
        throw error
      }
    },
    
    async createTask(taskData) {
      this.loading = true
      try {
        const response = await api.createTask(taskData)
        await this.fetchTasks({ cycle_id: taskData.cycle_id })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建训练任务失败'
        console.error('创建训练任务失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateTask(id, taskData) {
      this.loading = true
      try {
        const response = await api.updateTask(id, taskData)
        await this.fetchTasks({ cycle_id: taskData.cycle_id })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新训练任务失败'
        console.error('更新训练任务失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async completeTask(id, completionData) {
      this.loading = true
      try {
        const response = await api.completeTask(id, completionData)
        // 重新获取任务列表以更新状态
        const taskToUpdate = this.tasks.find(task => task.id === id)
        if (taskToUpdate && taskToUpdate.cycle_id) {
          await this.fetchTasks({ cycle_id: taskToUpdate.cycle_id })
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '完成训练任务失败'
        console.error('完成训练任务失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 获取今日任务
    async fetchTodayTasks(cycleId) {
      if (!cycleId) return []
      
      try {
        // 获取今天是星期几
        const today = new Date()
        const dayOfWeek = today.getDay() // 0是周日，1-6是周一到周六
        
        // 获取今天的日期字符串
        const year = today.getFullYear()
        const month = String(today.getMonth() + 1).padStart(2, '0')
        const day = String(today.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${day}`
        
        // 获取今天的任务
        const response = await api.getTasks({
          cycle_id: cycleId,
          day_of_week: dayOfWeek,
          date: dateStr
        })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取今日任务失败'
        console.error('获取今日任务失败:', error)
        return []
      }
    }
  }
})