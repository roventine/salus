<template>
    <div class="dashboard-container">
      <div class="page-header">
  
        <el-select v-model="selectedCycle" placeholder="选择康复周期" @change="fetchStats">
          <el-option
            v-for="cycle in cycles"
            :key="cycle.id"
            :label="cycle.name"
            :value="cycle.id"
          />
        </el-select>
      </div>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.total_completions || 0 }}</div>
            <div class="stat-label">已完成任务</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.total_sets || 0 }}</div>
            <div class="stat-label">总组数</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ completionRate }}%</div>
            <div class="stat-label">完成率</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ currentDay }}/{{ totalDays }}</div>
            <div class="stat-label">天数进度</div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="chart-row">
        <el-col :span="12">
          <el-card class="chart-card">
            <div class="chart-title">每日完成情况</div>
            <div ref="dailyChart" class="chart"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <div class="chart-title">运动类型分布</div>
            <div ref="exerciseChart" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="tasks-card">
        <template #header>
          <div class="card-header">
            <span>今日训练任务</span>
            <el-button type="text" @click="fetchTodayTasks">刷新</el-button>
          </div>
        </template>
        <el-table :data="todayTasks" style="width: 100%">
          <el-table-column prop="scheduled_time" label="时间" width="100">
            <template #default="scope">
              {{ formatTime(scope.row.scheduled_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="exercise_name" label="运动名称" />
          <el-table-column prop="sets" label="组数" width="80" />
          <el-table-column prop="is_completed" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_completed ? 'success' : 'info'">
                {{ scope.row.is_completed ? '已完成' : '未完成' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="completeTask(scope.row)"
                :disabled="scope.row.is_completed">
                完成
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  setup() {
    const API_BASE_URL = 'http://localhost:5000'
    
    // 数据
    const cycles = ref([])
    const selectedCycle = ref('')
    const stats = ref({
      total_completions: 0,
      total_sets: 0,
      exercise_stats: [],
      date_stats: []
    })
    const todayTasks = ref([])
    
    // 图表实例
    let dailyChartInstance = null
    let exerciseChartInstance = null
    
    // DOM引用
    const dailyChart = ref(null)
    const exerciseChart = ref(null)
    
    // 计算属性
    const completionRate = computed(() => {
      if (!selectedCycle.value || !currentCycle.value) return 0
      
      const totalTasks = todayTasks.value.length
      if (totalTasks === 0) return 0
      
      const completedTasks = todayTasks.value.filter(task => task.is_completed).length
      return Math.round((completedTasks / totalTasks) * 100)
    })
    
    const currentCycle = computed(() => {
      if (!selectedCycle.value) return null
      return cycles.value.find(cycle => cycle.id === selectedCycle.value)
    })
    
    const currentDay = computed(() => {
      if (!currentCycle.value) return 0
      
      const startDate = new Date(currentCycle.value.start_date)
      const today = new Date()
      
      // 计算天数差
      const diffTime = Math.abs(today - startDate)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      return Math.min(diffDays, totalDays.value)
    })
    
    const totalDays = computed(() => {
      if (!currentCycle.value) return 0
      
      const startDate = new Date(currentCycle.value.start_date)
      const endDate = new Date(currentCycle.value.end_date)
      
      // 计算总天数
      const diffTime = Math.abs(endDate - startDate)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    })
    
    // 方法
    const fetchCycles = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/cycles`)
        cycles.value = response.data
        if (cycles.value.length > 0 && !selectedCycle.value) {
          selectedCycle.value = cycles.value[0].id
          fetchStats()
          fetchTodayTasks()
        }
      } catch (error) {
        console.error('获取康复周期失败:', error)
        ElMessage.error('获取康复周期失败')
      }
    }
    
    const fetchStats = async () => {
      if (!selectedCycle.value) return
      
      try {
        const response = await axios.get(`${API_BASE_URL}/completions/stats`, {
          params: { cycle_id: selectedCycle.value }
        })
        stats.value = response.data
        
        // 更新图表
        renderDailyChart()
        renderExerciseChart()
      } catch (error) {
        console.error('获取统计数据失败:', error)
        ElMessage.error('获取统计数据失败')
      }
    }
    
    const fetchTodayTasks = async () => {
      if (!selectedCycle.value) return
      
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
        const response = await axios.get(`${API_BASE_URL}/tasks`, {
          params: {
            cycle_id: selectedCycle.value,
            day_of_week: dayOfWeek,
            date: dateStr
          }
        })
        
        todayTasks.value = response.data
      } catch (error) {
        console.error('获取今日任务失败:', error)
        ElMessage.error('获取今日任务失败')
      }
    }
    
    const completeTask = async (task) => {
      try {
        await axios.post(`${API_BASE_URL}/completions`, {
          task_id: task.id,
          actual_sets: task.sets
        })
        
        ElMessage.success('任务已完成')
        fetchTodayTasks()
        fetchStats()
      } catch (error) {
        console.error('完成任务失败:', error)
        ElMessage.error('完成任务失败')
      }
    }
    
    const renderDailyChart = () => {
      if (!dailyChart.value) return
      
      if (!dailyChartInstance) {
        dailyChartInstance = echarts.init(dailyChart.value)
      }
      
      const dateStats = stats.value.date_stats || []
      const dates = dateStats.map(item => item.date)
      const counts = dateStats.map(item => item.count)
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: dates
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: counts,
            type: 'line',
            smooth: true,
            areaStyle: {}
          }
        ]
      }
      
      dailyChartInstance.setOption(option)
    }
    
    const renderExerciseChart = () => {
      if (!exerciseChart.value) return
      
      if (!exerciseChartInstance) {
        exerciseChartInstance = echarts.init(exerciseChart.value)
      }
      
      const exerciseStats = stats.value.exercise_stats || []
      const data = exerciseStats.map(item => ({
        name: item.name,
        value: item.count
      }))
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [
          {
            name: '运动类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '16',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data
          }
        ]
      }
      
      exerciseChartInstance.setOption(option)
    }
    
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      return timeStr.substring(0, 5) // 只显示小时和分钟
    }
    
    // 窗口大小变化时重绘图表
    const handleResize = () => {
      if (dailyChartInstance) {
        dailyChartInstance.resize()
      }
      if (exerciseChartInstance) {
        exerciseChartInstance.resize()
      }
    }
    
    // 生命周期钩子
    onMounted(() => {
      fetchCycles()
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      if (dailyChartInstance) {
        dailyChartInstance.dispose()
      }
      if (exerciseChartInstance) {
        exerciseChartInstance.dispose()
      }
    })
    
    return {
      cycles,
      selectedCycle,
      stats,
      todayTasks,
      dailyChart,
      exerciseChart,
      completionRate,
      currentDay,
      totalDays,
      fetchStats,
      fetchTodayTasks,
      completeTask,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  margin-bottom: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}

.chart {
  height: 300px;
}

.tasks-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>