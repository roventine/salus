<template>
  <div class="tasks-container">
    <div class="page-header">
      <h2>训练任务</h2>
      <div class="header-actions">
        <el-select v-model="selectedCycle" placeholder="选择康复周期" @change="fetchTasks">
          <el-option
            v-for="cycle in cycles"
            :key="cycle.id"
            :label="cycle.name"
            :value="cycle.id"
          />
        </el-select>
        <el-button type="primary" @click="openDialog()" :disabled="!selectedCycle">
          新建训练任务
        </el-button>
      </div>
    </div>
    
    <div class="filter-container">
      <el-radio-group v-model="dayFilter" @change="fetchTasks">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="1">周一</el-radio-button>
        <el-radio-button label="2">周二</el-radio-button>
        <el-radio-button label="3">周三</el-radio-button>
        <el-radio-button label="4">周四</el-radio-button>
        <el-radio-button label="5">周五</el-radio-button>
        <el-radio-button label="6">周六</el-radio-button>
        <el-radio-button label="0">周日</el-radio-button>
      </el-radio-group>
    </div>
    
    <el-table :data="tasks" style="width: 100%" v-loading="loading">
      <el-table-column label="日期" width="120">
        <template #default="scope">
          {{ scope.row.specific_date }}
        </template>
      </el-table-column>    
      <el-table-column label="星期" width="80">
        <template #default="scope">
          {{ getDayOfWeekLabel(scope.row.day_of_week) }}
        </template>
      </el-table-column>
      <el-table-column prop="scheduled_time" label="时间" width="100">
        <template #default="scope">
          {{ formatTime(scope.row.scheduled_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="exercise_name" label="运动名称" />
      <el-table-column prop="sets" label="组数" width="80" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button 
            type="primary" 
            size="small" 
            @click="completeTask(scope.row)"
            :disabled="scope.row.is_completed">
            完成
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
    
    <!-- 新建/编辑任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑训练任务' : '新建训练任务'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="星期" prop="day_of_week">
          <el-select v-model="form.day_of_week" placeholder="请选择星期">
            <el-option label="周一" :value="1" />
            <el-option label="周二" :value="2" />
            <el-option label="周三" :value="3" />
            <el-option label="周四" :value="4" />
            <el-option label="周五" :value="5" />
            <el-option label="周六" :value="6" />
            <el-option label="周日" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间" prop="scheduled_time">
          <el-time-picker
            v-model="form.scheduled_time"
            format="HH:mm"
            placeholder="选择时间"
          />
        </el-form-item>
        <el-form-item label="运动类型" prop="exercise_id">
          <el-select v-model="form.exercise_id" placeholder="请选择运动类型">
            <el-option
              v-for="exercise in exercises"
              :key="exercise.id"
              :label="exercise.name"
              :value="exercise.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="组数" prop="sets">
          <el-input-number v-model="form.sets" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            placeholder="请输入备注信息"
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
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Tasks',
  setup() {
    const API_BASE_URL = 'http://localhost:5000'
    
    // 数据
    const cycles = ref([])
    const exercises = ref([])
    const tasks = ref([])
    const selectedCycle = ref('')
    const dayFilter = ref('all')
    const loading = ref(false)
    
    // 表单相关
    const dialogVisible = ref(false)
    const isEditing = ref(false)
    const form = reactive({
      id: null,
      cycle_id: null,
      exercise_id: null,
      day_of_week: null,
      scheduled_time: '',
      sets: 30,
      notes: ''
    })
    const rules = {
      day_of_week: [{ required: true, message: '请选择星期', trigger: 'change' }],
      scheduled_time: [{ required: true, message: '请选择时间', trigger: 'change' }],
      exercise_id: [{ required: true, message: '请选择运动类型', trigger: 'change' }],
      sets: [{ required: true, message: '请输入组数', trigger: 'blur' }]
    }
    const formRef = ref(null)
    
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
    const fetchCycles = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/cycles`)
        cycles.value = response.data
        if (cycles.value.length > 0 && !selectedCycle.value) {
          selectedCycle.value = cycles.value[0].id
          fetchTasks()
        }
      } catch (error) {
        console.error('获取康复周期失败:', error)
        ElMessage.error('获取康复周期失败')
      }
    }
    
    const fetchExercises = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/exercises`)
        exercises.value = response.data
      } catch (error) {
        console.error('获取运动类型失败:', error)
        ElMessage.error('获取运动类型失败')
      }
    }
    
    const fetchTasks = async () => {
      if (!selectedCycle.value) return
      
      loading.value = true
      try {
        const params = { cycle_id: selectedCycle.value }
        if (dayFilter.value !== 'all') {
          params.day_of_week = dayFilter.value
        }
        
        const response = await axios.get(`${API_BASE_URL}/tasks`, { params })
        tasks.value = response.data
      } catch (error) {
        console.error('获取训练任务失败:', error)
        ElMessage.error('获取训练任务失败')
      } finally {
        loading.value = false
      }
    }
    
    const openDialog = (task = null) => {
      if (task) {
        // 编辑模式
        isEditing.value = true
        form.id = task.id
        form.cycle_id = task.cycle_id
        form.exercise_id = task.exercise_id
        form.day_of_week = task.day_of_week
        
        // 处理时间格式
        if (task.scheduled_time) {
          const [hours, minutes] = task.scheduled_time.split(':')
          const date = new Date()
          date.setHours(parseInt(hours))
          date.setMinutes(parseInt(minutes))
          form.scheduled_time = date
        } else {
          form.scheduled_time = null
        }
        
        form.sets = task.sets
        form.notes = task.notes || ''
      } else {
        // 新建模式
        isEditing.value = false
        form.id = null
        form.cycle_id = selectedCycle.value
        form.exercise_id = exercises.value.length > 0 ? exercises.value[0].id : null
        form.day_of_week = 1
        form.scheduled_time = null
        form.sets = 30
        form.notes = ''
      }
      
      dialogVisible.value = true
    }
    
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid) => {
        if (valid) {
          // 格式化时间
          let formattedTime = null
          if (form.scheduled_time) {
            const hours = form.scheduled_time.getHours().toString().padStart(2, '0')
            const minutes = form.scheduled_time.getMinutes().toString().padStart(2, '0')
            formattedTime = `${hours}:${minutes}:00`
          }
          
          const taskData = {
            cycle_id: form.cycle_id,
            exercise_id: form.exercise_id,
            day_of_week: form.day_of_week,
            scheduled_time: formattedTime,
            sets: form.sets,
            notes: form.notes
          }
          
          try {
            if (isEditing.value) {
              // 更新任务
              await axios.put(`${API_BASE_URL}/tasks/${form.id}`, taskData)
              ElMessage.success('训练任务更新成功')
            } else {
              // 创建任务
              await axios.post(`${API_BASE_URL}/tasks`, taskData)
              ElMessage.success('训练任务创建成功')
            }
            
            dialogVisible.value = false
            fetchTasks()
          } catch (error) {
            console.error('保存训练任务失败:', error)
            ElMessage.error('保存训练任务失败')
          }
        }
      })
    }
    
    const confirmDelete = (task) => {
      ElMessageBox.confirm(
        '确定要删除这个训练任务吗？',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await axios.delete(`${API_BASE_URL}/tasks/${task.id}`)
          ElMessage.success('训练任务删除成功')
          fetchTasks()
        } catch (error) {
          console.error('删除训练任务失败:', error)
          ElMessage.error('删除训练任务失败')
        }
      }).catch(() => {
        // 用户取消删除
      })
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
            fetchTasks()
          } catch (error) {
            console.error('保存完成记录失败:', error)
            ElMessage.error('保存完成记录失败')
          }
        }
      })
    }
    
    const getDayOfWeekLabel = (day) => {
      const days = {
        0: '周日',
        1: '周一',
        2: '周二',
        3: '周三',
        4: '周四',
        5: '周五',
        6: '周六'
      }
      return days[day] || '每天'
    }
    
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      return timeStr.substring(0, 5) // 只显示小时和分钟
    }
    
    // 生命周期钩子
    onMounted(() => {
      fetchCycles()
      fetchExercises()
    })
    
    return {
      cycles,
      exercises,
      tasks,
      selectedCycle,
      dayFilter,
      loading,
      dialogVisible,
      isEditing,
      form,
      rules,
      formRef,
      completeDialogVisible,
      completeForm,
      completeRules,
      completeFormRef,
      fetchTasks,
      openDialog,
      submitForm,
      confirmDelete,
      completeTask,
      submitCompleteForm,
      getDayOfWeekLabel,
      formatTime
    }
  }
}
</script>

<style scoped>
.tasks-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-container {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>