import { defineStore } from 'pinia'
import api from '../api'

export const useCycleStore = defineStore('cycles', {
  state: () => ({
    cycles: [],
    currentCycle: null,
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchCycles() {
      this.loading = true
      try {
        const response = await api.getCycles()
        this.cycles = response.data
        this.error = null
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取康复周期失败'
        console.error('获取康复周期失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async getCycle(id) {
      this.loading = true
      try {
        const response = await api.getCycle(id)
        this.currentCycle = response.data
        this.error = null
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取康复周期详情失败'
        console.error('获取康复周期详情失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async createCycle(cycleData) {
      this.loading = true
      try {
        const response = await api.createCycle(cycleData)
        await this.fetchCycles()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建康复周期失败'
        console.error('创建康复周期失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateCycle(id, cycleData) {
      this.loading = true
      try {
        const response = await api.updateCycle(id, cycleData)
        await this.fetchCycles()
        if (this.currentCycle && this.currentCycle.id === id) {
          await this.getCycle(id)
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新康复周期失败'
        console.error('更新康复周期失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteCycle(id) {
      this.loading = true
      try {
        const response = await api.deleteCycle(id)
        await this.fetchCycles()
        if (this.currentCycle && this.currentCycle.id === id) {
          this.currentCycle = null
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '删除康复周期失败'
        console.error('删除康复周期失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 计算周期的总天数
    calculateDuration(startDate, endDate) {
      if (!startDate || !endDate) return 0
      
      const start = new Date(startDate)
      const end = new Date(endDate)
      return Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
    }
  }
})