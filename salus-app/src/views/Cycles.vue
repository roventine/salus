<template>
  <div class="cycles-container">
    <div class="page-header">
      <h2>康复周期管理</h2>
      <el-button type="primary" @click="openDialog()">
        新建康复周期
      </el-button>
    </div>
    
    <el-table :data="cycles" style="width: 100%" v-loading="loading">
      <el-table-column prop="name" label="周期名称" />
      <el-table-column prop="start_date" label="开始日期" width="120" />
      <el-table-column prop="end_date" label="结束日期" width="120" />
      <el-table-column label="持续时间" width="120">
        <template #default="scope">
          {{ calculateDuration(scope.row.start_date, scope.row.end_date) }}天
        </template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" show-overflow-tooltip />
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button type="primary" size="small" @click="viewTasks(scope.row)">
            查看任务
          </el-button>
          <el-button type="success" size="small" @click="openBatchDialog(scope.row)">
            批量配置
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
    
    <!-- 新建/编辑周期对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑康复周期' : '新建康复周期'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="周期名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入周期名称" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            placeholder="选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="date"
            placeholder="选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
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
    
    <!-- 批量配置对话框 -->
    <el-dialog
      v-model="batchDialogVisible"
      title="批量配置训练计划"
      width="600px"
    >
      <div class="batch-config-container">
        <div class="batch-header">
          <h3>{{ currentCycle.name }}</h3>
          <p>{{ currentCycle.start_date }} 至 {{ currentCycle.end_date }}</p>
        </div>
        
        <el-form
          ref="batchFormRef"
          :model="batchForm"
          :rules="batchRules"
          label-width="120px"
        >
          <el-form-item label="配置时间段" required>
            <el-row :gutter="10">
              <el-col :span="11">
                <el-form-item prop="start_week">
                  <el-select v-model="batchForm.start_week" placeholder="开始周">
                    <el-option
                      v-for="week in weekOptions"
                      :key="week.value"
                      :label="week.label"
                      :value="week.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="2" class="text-center">至</el-col>
              <el-col :span="11">
                <el-form-item prop="end_week">
                  <el-select v-model="batchForm.end_week" placeholder="结束周">
                    <el-option
                      v-for="week in weekOptions"
                      :key="week.value"
                      :label="week.label"
                      :value="week.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form-item>
          
          <el-form-item label="选择星期" prop="days">
            <el-checkbox-group v-model="batchForm.days">
              <el-checkbox :label="1">周一</el-checkbox>
              <el-checkbox :label="2">周二</el-checkbox>
              <el-checkbox :label="3">周三</el-checkbox>
              <el-checkbox :label="4">周四</el-checkbox>
              <el-checkbox :label="5">周五</el-checkbox>
              <el-checkbox :label="6">周六</el-checkbox>
              <el-checkbox :label="0">周日</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <el-form-item label="训练时间" prop="scheduled_time">
            <el-time-picker
              v-model="batchForm.scheduled_time"
              format="HH:mm"
              placeholder="选择时间"
            />
          </el-form-item>
          
          <el-form-item label="运动类型" prop="exercise_id">
            <el-select v-model="batchForm.exercise_id" placeholder="请选择运动类型">
              <el-option
                v-for="exercise in exercises"
                :key="exercise.id"
                :label="exercise.name"
                :value="exercise.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="组数" prop="sets">
            <el-input-number v-model="batchForm.sets" :min="1" :max="100" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBatchForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Cycles',
  setup() {
    const API_BASE_URL = 'http://localhost:5000'
    const router = useRouter()
    
    // 数据
    const cycles = ref([])
    const exercises = ref([])
    const loading = ref(false)
    
    // 表单相关
    const dialogVisible = ref(false)
    const isEditing = ref(false)
    const form = reactive({
      id: null,
      name: '',
      start_date: '',
      end_date: '',
      notes: ''
    })
    const rules = {
      name: [{ required: true, message: '请输入周期名称', trigger: 'blur' }],
      start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
      end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
    }
    const formRef = ref(null)
    
    // 批量配置相关
    const batchDialogVisible = ref(false)
    const currentCycle = ref({})
    const batchForm = reactive({
      cycle_id: null,
      start_week: 1,
      end_week: 1,
      days: [],
      scheduled_time: '',
      exercise_id: null,
      sets: 30
    })
    const batchRules = {
      start_week: [{ required: true, message: '请选择开始周', trigger: 'change' }],
      end_week: [{ required: true, message: '请选择结束周', trigger: 'change' }],
      days: [{ type: 'array', required: true, message: '请至少选择一天', trigger: 'change' }],
      scheduled_time: [{ required: true, message: '请选择时间', trigger: 'change' }],
      exercise_id: [{ required: true, message: '请选择运动类型', trigger: 'change' }],
      sets: [{ required: true, message: '请输入组数', trigger: 'blur' }]
    }
    const batchFormRef = ref(null)
    
    // 计算属性
    const weekOptions = computed(() => {
      if (!currentCycle.value.start_date || !currentCycle.value.end_date) {
        return []
      }
      
      const start = new Date(currentCycle.value.start_date)
      const end = new Date(currentCycle.value.end_date)
      const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
      const totalWeeks = Math.ceil(totalDays / 7)
      
      return Array.from({ length: totalWeeks }, (_, i) => ({
        value: i + 1,
        label: `第${i + 1}周`
      }))
    })
    
    // 方法
    const fetchCycles = async () => {
      loading.value = true
      try {
        const response = await axios.get(`${API_BASE_URL}/cycles`)
        cycles.value = response.data
      } catch (error) {
        console.error('获取康复周期失败:', error)
        ElMessage.error('获取康复周期失败')
      } finally {
        loading.value = false
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
    
    const calculateDuration = (startDate, endDate) => {
      if (!startDate || !endDate) return 0
      
      const start = new Date(startDate)
      const end = new Date(endDate)
      return Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
    }
    
    const openDialog = (cycle = null) => {
      if (cycle) {
        // 编辑模式
        isEditing.value = true
        form.id = cycle.id
        form.name = cycle.name
        form.start_date = cycle.start_date
        form.end_date = cycle.end_date
        form.notes = cycle.notes || ''
      } else {
        // 新建模式
        isEditing.value = false
        form.id = null
        form.name = ''
        form.start_date = ''
        form.end_date = ''
        form.notes = ''
      }
      
      dialogVisible.value = true
    }
    
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            if (isEditing.value) {
              // 更新
              await axios.put(`${API_BASE_URL}/cycles/${form.id}`, {
                name: form.name,
                start_date: form.start_date,
                end_date: form.end_date,
                notes: form.notes
              })
              ElMessage.success('康复周期更新成功')
            } else {
              // 创建
              await axios.post(`${API_BASE_URL}/cycles`, {
                name: form.name,
                start_date: form.start_date,
                end_date: form.end_date,
                notes: form.notes
              })
              ElMessage.success('康复周期创建成功')
            }
            
            dialogVisible.value = false
            fetchCycles()
          } catch (error) {
            console.error('操作失败:', error)
            ElMessage.error(error.response?.data?.error || '操作失败')
          }
        }
      })
    }
    
    const confirmDelete = (cycle) => {
      ElMessageBox.confirm(
        '此操作将永久删除该康复周期及其关联的训练任务，是否继续？',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await axios.delete(`${API_BASE_URL}/cycles/${cycle.id}`)
          ElMessage.success('删除成功')
          fetchCycles()
        } catch (error) {
          console.error('删除失败:', error)
          ElMessage.error(error.response?.data?.error || '删除失败')
        }
      }).catch(() => {
        ElMessage.info('已取消删除')
      })
    }
    
    const viewTasks = (cycle) => {
      router.push({
        path: '/tasks',
        query: { cycle_id: cycle.id }
      })
    }
    
    const openBatchDialog = (cycle) => {
      currentCycle.value = cycle
      batchForm.cycle_id = cycle.id
      batchForm.start_week = 1
      batchForm.end_week = 1
      batchForm.days = []
      batchForm.scheduled_time = ''
      batchForm.exercise_id = null
      batchForm.sets = 30
      
      batchDialogVisible.value = true
    }
    
    const submitBatchForm = async () => {
      if (!batchFormRef.value) return
      
      await batchFormRef.value.validate(async (valid) => {
        if (valid) {
          if (batchForm.start_week > batchForm.end_week) {
            ElMessage.error('开始周不能大于结束周')
            return
          }
          
          try {
            // 格式化时间
            const timeStr = batchForm.scheduled_time instanceof Date
              ? `${batchForm.scheduled_time.getHours().toString().padStart(2, '0')}:${batchForm.scheduled_time.getMinutes().toString().padStart(2, '0')}:00`
              : batchForm.scheduled_time
            
            // 批量创建任务
            await axios.post(`${API_BASE_URL}/tasks/batch`, {
              cycle_id: batchForm.cycle_id,
              start_week: batchForm.start_week,
              end_week: batchForm.end_week,
              days: batchForm.days,
              scheduled_time: timeStr,
              exercise_id: batchForm.exercise_id,
              sets: batchForm.sets
            })
            
            ElMessage.success('批量配置成功')
            batchDialogVisible.value = false
          } catch (error) {
            console.error('批量配置失败:', error)
            ElMessage.error(error.response?.data?.error || '批量配置失败')
          }
        }
      })
    }
    
    onMounted(() => {
      fetchCycles()
      fetchExercises()
    })
    
    return {
      cycles,
      exercises,
      loading,
      dialogVisible,
      isEditing,
      form,
      rules,
      formRef,
      batchDialogVisible,
      currentCycle,
      batchForm,
      batchRules,
      batchFormRef,
      weekOptions,
      calculateDuration,
      openDialog,
      submitForm,
      confirmDelete,
      viewTasks,
      openBatchDialog,
      submitBatchForm
    }
  }
}
</script>

<style scoped>
.cycles-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.batch-header {
  margin-bottom: 20px;
  text-align: center;
}

.batch-header h3 {
  margin-bottom: 5px;
}

.text-center {
  text-align: center;
  line-height: 32px;
}

.el-form-item {
  margin-bottom: 22px;
}

.unit {
  margin-left: 8px;
}
</style>