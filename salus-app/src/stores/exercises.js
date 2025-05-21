import { defineStore } from 'pinia'
import api from '../api'

export const useExerciseStore = defineStore('exercises', {
  state: () => ({
    exercises: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchExercises() {
      this.loading = true
      try {
        const response = await api.getExercises()
        this.exercises = response.data
        this.error = null
      } catch (error) {
        this.error = error.response?.data?.error || '获取运动类型失败'
        console.error('获取运动类型失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async createExercise(exerciseData) {
      this.loading = true
      try {
        const response = await api.createExercise(exerciseData)
        await this.fetchExercises()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建运动类型失败'
        console.error('创建运动类型失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateExercise(id, exerciseData) {
      this.loading = true
      try {
        const response = await api.updateExercise(id, exerciseData)
        await this.fetchExercises()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新运动类型失败'
        console.error('更新运动类型失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteExercise(id) {
      this.loading = true
      try {
        const response = await api.deleteExercise(id)
        await this.fetchExercises()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '删除运动类型失败'
        console.error('删除运动类型失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})