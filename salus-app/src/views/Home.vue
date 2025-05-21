<template>
  <div class="home-container">
    <div class="welcome-section">
      <h2>欢迎使用术后康复训练管理系统</h2>
      <p>本系统帮助您规划和管理术后康复训练，提高康复效率</p>
    </div>
    
    <el-row :gutter="20" class="quick-access">
      <el-col :span="8">
        <el-card class="quick-card" @click="navigateTo('/dashboard')">
          <div class="card-icon">
            <el-icon><el-icon-odometer /></el-icon>
          </div>
          <div class="card-title">仪表盘</div>
          <div class="card-desc">查看康复进度和统计数据</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="quick-card" @click="navigateTo('/tasks')">
          <div class="card-icon">
            <el-icon><el-icon-calendar /></el-icon>
          </div>
          <div class="card-title">训练任务</div>
          <div class="card-desc">管理您的日常训练计划</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="quick-card" @click="navigateTo('/timer')">
          <div class="card-icon">
            <el-icon><el-icon-timer /></el-icon>
          </div>
          <div class="card-title">计时器</div>
          <div class="card-desc">使用Tabata计时器辅助训练</div>
        </el-card>
      </el-col>
    </el-row>
    
    <div class="section-title">
      <h3>今日训练任务</h3>
      <el-button type="text" @click="navigateTo('/tasks')">查看全部</el-button>
    </div>
    
    <el-card class="today-tasks" v-loading="loading">
      <div v-if="todayTasks.length === 0" class="empty-tasks">
        <el-empty description="今日暂无训练任务"></el-empty>
      </div>
      <el-timeline v-else>
        <el-timeline-item
          v-for="task in todayTasks"
          :key="task.id"
          :timestamp="formatTime(task.scheduled_time)"
          :type="getTimelineItemType(task)"
        >
          <el-card class="task-card">
            <div class="task-header">
              <span class="task-name">{{ task.exercise_name }}</span>
              <el-tag :type="task.is_completed ? 'success' : 'info'">
                {{ task.is_completed ? '已完成' : '未完成' }}
              </el-tag>
            </div>
            <div class="task-detail">
              <span>{{ task.sets }} 组</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="completeTask(task)"
                :disabled="task.is_completed">
                完成任务
              </el-button>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
    
    <!-- 完成任务对话框 -->
    <el-dialog
      v-model="completeDialogVisible"
      title="完成训练任务"
      width="500px"
    >
      <el-form
        ref="completeFormRef"
        :model="completeForm"
        :rules="completeRules"
        label-width="100px"
      >
        <el-form-item label="实际组数" prop="actual_sets">
          <el-input-number v-model="completeForm.actual_sets" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="completeForm.notes"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="completeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCompleteForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ElIconOdometer, ElIconCalendar, ElIconTimer } from '@element-plus/icons-vue'

export default {
  name: 'Home',
  components: {
    ElIconOdometer,
    ElIconCalendar,
    ElIconTimer
  },
  setup() {
    const API_BASE_URL = 'http://localhost:5000'
    const router = useRouter()
    
    // 数据
    const todayTasks = ref([])
    const loading = ref(false)
    
    // 完成任务相关
    const completeDialogVisible = ref(false)
    const completeForm = reactive({
      task_id: null,
      actual_sets: 0,
      notes: ''
    })
    const completeRules = {
      actual_sets: [{ required: true, message: '请输入实际完成组数', trigger: 'blur' }]
    }
    const completeFormRef = ref(null)
    
    // 方法
    const fetchTodayTasks = async () => {
      loading.value = true
      try {
        const today = new Date().toISOString().split('T')[0]
        const response = await axios.get(`${API_BASE_URL}/tasks`, {
          params: { date: today }
        })
        todayTasks.value = response.data
      } catch (error) {
        console.error('获取今日任务失败:', error)
        ElMessage.error('获取今日任务失败')
      } finally {
        loading.value = false
      }
    }
    
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      return timeStr.substring(0, 5)
    }
    
    const getTimelineItemType = (task) => {
      if (task.is_completed) {
        return 'success'
      }
      
      const now = new Date()
      const taskTime = new Date()
      const [hours, minutes] = task.scheduled_time.split(':').map(Number)
      taskTime.setHours(hours, minutes, 0)
      
      // 如果任务时间已过但未完成
      if (now > taskTime) {
        return 'danger'
      }
      
      // 如果任务时间在未来1小时内
      const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000)
      if (taskTime <= oneHourLater) {
        return 'warning'
      }
      
      return 'primary'
    }
    
    const navigateTo = (path) => {
      router.push(path)
    }
    
    const completeTask = (task) => {
      completeForm.task_id = task.id
      completeForm.actual_sets = task.sets
      completeForm.notes = ''
      completeDialogVisible.value = true
    }
    
    const submitCompleteForm = async () => {
      if (!completeFormRef.value) return
      
      await completeFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            await axios.post(`${API_BASE_URL}/completions`, {
              task_id: completeForm.task_id,
              actual_sets: completeForm.actual_sets,
              notes: completeForm.notes
            })
            
            ElMessage.success('任务完成记录已保存')
            completeDialogVisible.value = false
            fetchTodayTasks()
          } catch (error) {
            console.error('保存完成记录失败:', error)
            ElMessage.error(error.response?.data?.error || '保存完成记录失败')
          }
        }
      })
    }
    
    onMounted(() => {
      fetchTodayTasks()
    })
    
    return {
      todayTasks,
      loading,
      completeDialogVisible,
      completeForm,
      completeRules,
      completeFormRef,
      formatTime,
      getTimelineItemType,
      navigateTo,
      completeTask,
      submitCompleteForm
    }
  }
}
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-section h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.welcome-section p {
  color: #666;
  font-size: 16px;
}

.quick-access {
  margin-bottom: 30px;
}

.quick-card {
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.card-icon {
  font-size: 40px;
  margin-bottom: 15px;
  color: #409EFF;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.card-desc {
  color: #666;
  text-align: center;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-title h3 {
  margin: 0;
  font-size: 18px;
}

.today-tasks {
  margin-bottom: 30px;
}

.empty-tasks {
  padding: 30px 0;
  text-align: center;
}

.task-card {
  margin-bottom: 10px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-name {
  font-weight: bold;
}

.task-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #666;
}
</style>