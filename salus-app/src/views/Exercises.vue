<template>
  <div class="exercises-container">
    <div class="page-header">
      <h2>运动管理</h2>
      <el-button type="primary" @click="openDialog()">
        新建运动
      </el-button>
    </div>
    
    <el-table :data="exercises" style="width: 100%" v-loading="loading">
      <el-table-column prop="name" label="运动名称" />
      <el-table-column prop="duration_sec" label="运动时长(秒)" width="120" />
      <el-table-column prop="rest_sec" label="休息时长(秒)" width="120" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column label="操作" width="300">
        <template #default="scope">
          <el-button type="primary" size="small" @click="openTimerDialog(scope.row)">
            计时器
          </el-button>
          <el-button type="warning" size="small" @click="openDialog(scope.row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="confirmDelete(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 新建/编辑运动类型对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑运动类型' : '新建运动类型'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="运动名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入运动名称" />
        </el-form-item>
        <el-form-item label="运动时长" prop="duration_sec">
          <el-input-number v-model="form.duration_sec" :min="1" :max="60" />
          <span class="unit">秒</span>
        </el-form-item>
        <el-form-item label="休息时长" prop="rest_sec">
          <el-input-number v-model="form.rest_sec" :min="1" :max="60" />
          <span class="unit">秒</span>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入运动描述"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- Tabata计时器对话框 -->
    <el-dialog
      v-model="timerDialogVisible"
      title="Tabata计时器"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="!timerRunning"
    >
      <div class="timer-container">
        <div class="timer-header">
          <h3>{{ currentExercise.name }}</h3>
          <div class="timer-sets">组数: {{ currentSet }}/{{ totalSets }}</div>
        </div>
        
        <div class="timer-display" :class="{ 'rest-mode': isRestPhase }">
          <div class="timer-phase">{{ isRestPhase ? '休息' : '运动' }}</div>
          <div class="timer-countdown">{{ formatCountdown(countdown) }}</div>
          <el-progress 
            :percentage="progressPercentage" 
            :color="isRestPhase ? '#67C23A' : '#409EFF'"
          />
        </div>
        
        <div class="timer-controls">
          <el-button 
            type="primary" 
            size="large" 
            @click="toggleTimer"
            :icon="timerRunning ? 'Pause' : 'VideoPlay'"
          >
            {{ timerRunning ? '暂停' : '开始' }}
          </el-button>
          <el-button 
            type="danger" 
            size="large" 
            @click="resetTimer"
            :disabled="!timerStarted"
          >
            重置
          </el-button>
        </div>
        
        <div class="timer-settings">
          <div class="setting-item">
            <span>组数:</span>
            <el-input-number v-model="totalSets" :min="1" :max="100" :disabled="timerRunning" />
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Exercises',
  setup() {
    const API_BASE_URL = 'http://localhost:5000'
    
    // 数据
    const exercises = ref([])
    const loading = ref(false)
    
    // 表单相关
    const dialogVisible = ref(false)
    const isEditing = ref(false)
    const form = reactive({
      id: null,
      name: '',
      duration_sec: 5,
      rest_sec: 5,
      description: ''
    })
    const rules = {
      name: [{ required: true, message: '请输入运动名称', trigger: 'blur' }],
      duration_sec: [{ required: true, message: '请输入运动时长', trigger: 'blur' }],
      rest_sec: [{ required: true, message: '请输入休息时长', trigger: 'blur' }]
    }
    const formRef = ref(null)
    
    // 计时器相关
    const timerDialogVisible = ref(false)
    const currentExercise = ref({})
    const timerRunning = ref(false)
    const timerStarted = ref(false)
    const isRestPhase = ref(false)
    const countdown = ref(0)
    const currentSet = ref(1)
    const totalSets = ref(30)
    let timerInterval = null
    
    // 计算属性
    const progressPercentage = computed(() => {
      if (isRestPhase.value) {
        return 100 - (countdown.value / currentExercise.value.rest_sec * 100)
      } else {
        return 100 - (countdown.value / currentExercise.value.duration_sec * 100)
      }
    })
    
    // 方法
    const fetchExercises = async () => {
      loading.value = true
      try {
        const response = await axios.get(`${API_BASE_URL}/exercises`)
        exercises.value = response.data
      } catch (error) {
        console.error('获取运动类型失败:', error)
        ElMessage.error('获取运动类型失败')
      } finally {
        loading.value = false
      }
    }
    
    const openDialog = (exercise = null) => {
      if (exercise) {
        // 编辑模式
        isEditing.value = true
        form.id = exercise.id
        form.name = exercise.name
        form.duration_sec = exercise.duration_sec
        form.rest_sec = exercise.rest_sec
        form.description = exercise.description || ''
      } else {
        // 新建模式
        isEditing.value = false
        form.id = null
        form.name = ''
        form.duration_sec = 5
        form.rest_sec = 5
        form.description = ''
      }
      
      dialogVisible.value = true
    }
    
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid) => {
        if (valid) {
          const exerciseData = {
            name: form.name,
            duration_sec: form.duration_sec,
            rest_sec: form.rest_sec,
            description: form.description
          }
          
          try {
            if (isEditing.value) {
              // 更新运动类型
              await axios.put(`${API_BASE_URL}/exercises/${form.id}`, exerciseData)
              ElMessage.success('运动类型更新成功')
            } else {
              // 创建运动类型
              await axios.post(`${API_BASE_URL}/exercises`, exerciseData)
              ElMessage.success('运动类型创建成功')
            }
            
            dialogVisible.value = false
            fetchExercises()
          } catch (error) {
            console.error('保存运动类型失败:', error)
            ElMessage.error('保存运动类型失败')
          }
        }
      })
    }
    
    const confirmDelete = (exercise) => {
      ElMessageBox.confirm(
        '确定要删除这个运动类型吗？',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await axios.delete(`${API_BASE_URL}/exercises/${exercise.id}`)
          ElMessage.success('运动类型删除成功')
          fetchExercises()
        } catch (error) {
          console.error('删除运动类型失败:', error)
          if (error.response && error.response.status === 400) {
            ElMessage.error('该运动类型已被训练任务引用，无法删除')
          } else {
            ElMessage.error('删除运动类型失败')
          }
        }
      }).catch(() => {
        // 用户取消删除
      })
    }
    
    // 计时器相关方法
    const openTimerDialog = (exercise) => {
      currentExercise.value = exercise
      resetTimer()
      timerDialogVisible.value = true
    }
    
    const toggleTimer = () => {
      if (!timerRunning.value) {
        startTimer()
      } else {
        pauseTimer()
      }
    }
    
    const startTimer = () => {
      timerRunning.value = true
      timerStarted.value = true
      
      if (!timerInterval) {
        timerInterval = setInterval(() => {
          if (countdown.value > 0) {
            countdown.value--
          } else {
            // 当前阶段结束
            if (isRestPhase.value) {
              // 休息结束，进入下一组
              currentSet.value++
              
              if (currentSet.value > totalSets.value) {
                // 所有组数完成
                playSound('complete')
                resetTimer()
                ElMessage.success('所有组数已完成！')
                return
              }
              
              // 进入运动阶段
              isRestPhase.value = false
              countdown.value = currentExercise.value.duration_sec
              playSound('exercise')
            } else {
              // 运动结束，进入休息阶段
              isRestPhase.value = true
              countdown.value = currentExercise.value.rest_sec
              playSound('rest')
            }
          }
        }, 1000)
      }
    }
    
    const pauseTimer = () => {
      timerRunning.value = false
      clearInterval(timerInterval)
      timerInterval = null
    }
    
    const resetTimer = () => {
      pauseTimer()
      timerRunning.value = false
      timerStarted.value = false
      isRestPhase.value = false
      currentSet.value = 1
      countdown.value = currentExercise.value.duration_sec
    }
    
    const formatCountdown = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    
    const playSound = (type) => {
      let audio = new Audio()
      
      switch(type) {
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
        console.warn('无法播放音频:', error)
      })
    }
    
    // 组件卸载时清理计时器
    onUnmounted(() => {
      if (timerInterval) {
        clearInterval(timerInterval)
      }
    })
    
    // 初始化
    onMounted(() => {
      fetchExercises()
    })
    
    return {
      exercises,
      loading,
      dialogVisible,
      timerDialogVisible,
      formRef,
      form,
      rules,
      openDialog,
      submitForm,
      confirmDelete,
      currentExercise,
      timerRunning,
      timerStarted,
      isRestPhase,
      countdown,
      currentSet,
      totalSets,
      progressPercentage,
      openTimerDialog,
      toggleTimer,
      resetTimer,
      formatCountdown
    }
  }
}
</script>

<style scoped>
.exercises-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.unit {
  margin-left: 8px;
}

.timer-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.timer-header {
  text-align: center;
  margin-bottom: 20px;
}

.timer-sets {
  font-size: 16px;
  color: #606266;
}

.timer-display {
  width: 100%;
  padding: 30px;
  border-radius: 8px;
  background-color: #ecf5ff;
  text-align: center;
  margin-bottom: 20px;
}

.timer-display.rest-mode {
  background-color: #f0f9eb;
}

.timer-phase {
  font-size: 18px;
  margin-bottom: 10px;
}

.timer-countdown {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 15px;
}

.timer-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.timer-settings {
  width: 100%;
  padding: 15px;
  border-top: 1px solid #ebeef5;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
</style>