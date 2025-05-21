<template>
    <div class="timer-container">
      <div class="timer-header">
        <h2>Tabata计时器</h2>
      </div>
      
      <div class="timer-config" v-if="!isRunning">
        <el-form label-width="120px">
          <el-form-item label="选择运动">
            <el-select v-model="selectedExercise" placeholder="请选择运动" @change="handleExerciseChange">
              <el-option
                v-for="exercise in exerciseStore.exercises"
                :key="exercise.id"
                :label="exercise.name"
                :value="exercise.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="运动时长">
            <el-input-number v-model="exerciseDuration" :min="1" :max="60" />
            <span class="unit">秒</span>
          </el-form-item>
          
          <el-form-item label="休息时长">
            <el-input-number v-model="restDuration" :min="0" :max="60" />
            <span class="unit">秒</span>
          </el-form-item>
          
          <el-form-item label="组数">
            <el-input-number v-model="sets" :min="1" :max="100" />
            <span class="unit">组</span>
          </el-form-item>
        </el-form>
        
        <el-button type="primary" size="large" @click="startTimer">开始训练</el-button>
      </div>
      
      <div class="timer-display" v-else>
        <div class="timer-status">{{ isResting ? '休息' : '运动' }}</div>
        <div class="timer-time">{{ formatTime(currentTime) }}</div>
        <div class="timer-progress">
          <el-progress 
            :percentage="progressPercentage" 
            :color="isResting ? '#67C23A' : '#409EFF'"
            :stroke-width="20"
          />
        </div>
        <div class="timer-sets">
          <span>当前组数: {{ currentSet }} / {{ sets }}</span>
        </div>
        <div class="timer-controls">
          <el-button type="warning" @click="pauseTimer" v-if="!isPaused">暂停</el-button>
          <el-button type="primary" @click="resumeTimer" v-else>继续</el-button>
          <el-button type="danger" @click="stopTimer">停止</el-button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { useExerciseStore } from '../stores/exercises'
  import { ElMessage } from 'element-plus'
  
  const exerciseStore = useExerciseStore()
  
  // 计时器状态
  const isRunning = ref(false)
  const isPaused = ref(false)
  const isResting = ref(false)
  const currentTime = ref(0)
  const currentSet = ref(1)
  const timerInterval = ref(null)
  
  // 计时器配置
  const selectedExercise = ref(null)
  const exerciseDuration = ref(5)
  const restDuration = ref(5)
  const sets = ref(30)
  
  // 计算属性
  const progressPercentage = computed(() => {
    const totalDuration = isResting.value ? restDuration.value : exerciseDuration.value
    return Math.round((1 - currentTime.value / totalDuration) * 100)
  })
  
  // 生命周期钩子
  onMounted(async () => {
    await exerciseStore.fetchExercises()
    if (exerciseStore.exercises.length > 0) {
      selectedExercise.value = exerciseStore.exercises[0].id
      handleExerciseChange(selectedExercise.value)
    }
  })
  
  onUnmounted(() => {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
    }
  })
  
  // 方法
  const handleExerciseChange = (exerciseId) => {
    const exercise = exerciseStore.exercises.find(e => e.id === exerciseId)
    if (exercise) {
      exerciseDuration.value = exercise.duration_sec
      restDuration.value = exercise.rest_sec
    }
  }
  
  const formatTime = (seconds) => {
    return seconds.toString().padStart(2, '0')
  }
  
  const startTimer = () => {
    if (!selectedExercise.value) {
      ElMessage.warning('请先选择一个运动')
      return
    }
    
    isRunning.value = true
    isPaused.value = false
    isResting.value = false
    currentSet.value = 1
    currentTime.value = exerciseDuration.value
    
    runTimer()
  }
  
  const runTimer = () => {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
    }
    
    timerInterval.value = setInterval(() => {
      if (currentTime.value > 0) {
        currentTime.value--
      } else {
        // 当前阶段结束
        if (isResting.value) {
          // 休息结束，开始下一组运动
          currentSet.value++
          if (currentSet.value > sets.value) {
            // 所有组数完成
            playSound('complete')
            stopTimer()
            ElMessage.success('恭喜！所有训练组数已完成')
            return
          }
          isResting.value = false
          currentTime.value = exerciseDuration.value
          playSound('exercise')
        } else {
          // 运动结束，开始休息
          isResting.value = true
          currentTime.value = restDuration.value
          playSound('rest')
        }
      }
    }, 1000)
  }
  
  const pauseTimer = () => {
    isPaused.value = true
    clearInterval(timerInterval.value)
  }
  
  const resumeTimer = () => {
    isPaused.value = false
    runTimer()
  }
  
  const stopTimer = () => {
    isRunning.value = false
    isPaused.value = false
    clearInterval(timerInterval.value)
  }
  
  const playSound = (type) => {
    // 简单的声音提示实现
    const audio = new Audio()
    
    switch (type) {
      case 'exercise':
        audio.src = '/sounds/exercise.mp3'
        break
      case 'rest':
        audio.src = '/sounds/rest.mp3'
        break
      case 'complete':
        audio.src = '/sounds/complete.mp3'
        break
    }
    
    audio.play().catch(error => {
      console.error('播放声音失败:', error)
    })
  }
  </script>
  
  <style scoped>
  .timer-container {
    padding: 20px;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .timer-header {
    margin-bottom: 30px;
    text-align: center;
  }
  
  .timer-config {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .timer-display {
    background-color: #f9f9f9;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    text-align: center;
  }
  
  .timer-status {
    font-size: 24px;
    margin-bottom: 10px;
    font-weight: bold;
  }
  
  .timer-time {
    font-size: 72px;
    font-weight: bold;
    margin-bottom: 20px;
  }
  
  .timer-progress {
    margin-bottom: 20px;
  }
  
  .timer-sets {
    font-size: 18px;
    margin-bottom: 20px;
  }
  
  .timer-controls {
    display: flex;
    justify-content: center;
    gap: 10px;
  }
  
  .unit {
    margin-left: 5px;
  }
  </style>