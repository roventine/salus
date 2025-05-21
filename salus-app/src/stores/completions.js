import { defineStore } from 'pinia'
import api from '../api'

export const useCompletionStore = defineStore('completions', {
  state: () => ({
    completions: [],
    stats: null,
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchCompletions(params = {}) {
      this.loading = true
      try {
        const response = await api.getCompletions(params)
        this.completions = response.data
        this.error = null
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取完成记录失败'
        console.error('获取完成记录失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async getCompletion(id) {
      try {
        const response = await api.getCompletion(id)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取完成记录详情失败'
        console.error('获取完成记录详情失败:', error)
        throw error
      }
    },
    
    async createCompletion(completionData) {
      this.loading = true
      try {
        const response = await api.createCompletion(completionData)
        await this.fetchCompletions({ cycle_id: completionData.cycle_id })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建完成记录失败'
        console.error('创建完成记录失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateCompletion(id, completionData) {
      this.loading = true
      try {
        const response = await api.updateCompletion(id, completionData)
        await this.fetchCompletions({ cycle_id: completionData.cycle_id })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新完成记录失败'
        console.error('更新完成记录失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteCompletion(id, cycleId) {
      this.loading = true
      try {
        const response = await api.deleteCompletion(id)
        if (cycleId) {
          await this.fetchCompletions({ cycle_id: cycleId })
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '删除完成记录失败'
        console.error('删除完成记录失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchStats(params = {}) {
      this.loading = true
      try {
        const response = await api.getCompletionStats(params)
        this.stats = response.data
        this.error = null
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取统计数据失败'
        console.error('获取统计数据失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})