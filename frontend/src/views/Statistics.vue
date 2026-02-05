<template>
  <div class="statistics-page">
    <!-- 时间筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            value-format="YYYY-MM"
            @change="handleRangeChange"
          />
        </el-form-item>
        
        <el-form-item label="快捷选择">
          <el-radio-group v-model="quickRange" @change="handleQuickRange">
            <el-radio-button label="this_month">本月</el-radio-button>
            <el-radio-button label="last_month">上月</el-radio-button>
            <el-radio-button label="this_year">本年</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="8">
        <el-card class="stat-card income-card">
          <div class="stat-content">
            <el-icon><Money /></el-icon>
            <div class="stat-info">
              <div class="stat-label">总收入</div>
              <div class="stat-value text-success">
                +¥{{ (overview.total_income || 0).toFixed(2) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card expense-card">
          <div class="stat-content">
            <el-icon><Wallet /></el-icon>
            <div class="stat-info">
              <div class="stat-label">总支出</div>
              <div class="stat-value text-danger">
                -¥{{ (overview.total_expense || 0).toFixed(2) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card balance-card">
          <div class="stat-content">
            <el-icon><TrendCharts /></el-icon>
            <div class="stat-info">
              <div class="stat-label">结余</div>
              <div class="stat-value" :class="balanceClass">
                {{ balance >= 0 ? '+' : '' }}¥{{ balance.toFixed(2) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分类统计 & 项目统计 -->
    <el-row :gutter="20">
      <!-- 分类统计 -->
      <el-col :span="12">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>分类支出排行</span>
            </div>
          </template>
          
          <el-table :data="categoryStats" stripe style="width: 100%">
            <el-table-column prop="category_name" label="分类" width="120" />
            
            <el-table-column prop="amount" label="金额" width="120">
              <template #default="{ row }">
                ¥{{ row.amount.toFixed(2) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="percentage" label="占比">
              <template #default="{ row }">
                <el-progress 
                  :percentage="Math.round(row.percentage * 100)"
                  :stroke-width="8"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <!-- 项目统计 -->
      <el-col :span="12">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>项目支出排行</span>
            </div>
          </template>
          
          <el-table :data="projectStats" stripe style="width: 100%">
            <el-table-column prop="project_name" label="项目" width="120">
              <template #default="{ row }">
                {{ row.project_name || '无项目' }}
              </template>
            </el-table-column>
            
            <el-table-column label="收支">
              <template #default="{ row }">
                <span class="text-success">+¥{{ row.total_income.toFixed(2) }}</span>
                <span class="text-danger" style="margin-left: 8px">
                  -¥{{ row.total_expense.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            
            <el-table-column prop="balance" label="结余" width="100">
              <template #default="{ row }">
                <span :class="row.balance >= 0 ? 'text-success' : 'text-danger'">
                  {{ row.balance >= 0 ? '+' : '' }}¥{{ row.balance.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 月度趋势 -->
    <el-card class="trend-card">
      <template #header>
        <div class="card-header">
          <span>月度趋势</span>
        </div>
      </template>
      
      <el-table :data="monthlyStats" stripe style="width: 100%">
        <el-table-column prop="month" label="月份" width="100">
          <template #default="{ row }">
            {{ row.year }}-{{ String(row.month).padStart(2, '0') }}
          </template>
        </el-table-column>
        
        <el-table-column prop="total_income" label="收入" width="120">
          <template #default="{ row }">
            <span class="text-success">+¥{{ row.total_income.toFixed(2) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="total_expense" label="支出" width="120">
          <template #default="{ row }">
            <span class="text-danger">-¥{{ row.total_expense.toFixed(2) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="balance" label="结余">
          <template #default="{ row }">
            <span :class="row.balance >= 0 ? 'text-success' : 'text-danger'">
              {{ row.balance >= 0 ? '+' : '' }}¥{{ row.balance.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Money, Wallet, TrendCharts } from '@element-plus/icons-vue'
import { statistics } from '@/api/statistics'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const overview = ref({})
const categoryStats = ref([])
const projectStats = ref([])
const monthlyStats = ref([])

const filters = reactive({
  dateRange: []
})

const quickRange = ref('')

const now = new Date()
const thisYear = now.getFullYear()
const thisMonth = now.getMonth() + 1

const balance = computed(() => {
  return (overview.value.total_income || 0) - (overview.value.total_expense || 0)
})

const balanceClass = computed(() => {
  return balance.value >= 0 ? 'text-success' : 'text-danger'
})

onMounted(() => {
  // 默认本月
  quickRange.value = 'this_month'
  filters.dateRange = [`${thisYear}-01`, `${thisYear}-${String(thisMonth).padStart(2, '0')}`]
  fetchAllStats()
})

function handleQuickRange(value) {
  const year = thisYear
  const month = thisMonth
  
  if (value === 'this_month') {
    filters.dateRange = [`${year}-${String(month).padStart(2, '0')}`, `${year}-${String(month).padStart(2, '0')}`]
  } else if (value === 'last_month') {
    const lastMonth = month === 1 ? 12 : month - 1
    const lastYear = month === 1 ? year - 1 : year
    filters.dateRange = [`${lastYear}-${String(lastMonth).padStart(2, '0')}`, `${lastYear}-${String(lastMonth).padStart(2, '0')}`]
  } else if (value === 'this_year') {
    filters.dateRange = [`${year}-01`, `${year}-12`]
  }
  
  fetchAllStats()
}

function handleRangeChange() {
  quickRange.value = ''
  fetchAllStats()
}

async function fetchAllStats() {
  loading.value = true
  
  try {
    const [date_from, date_to] = filters.dateRange || []
    
    // 概览
    try {
      const overviewRes = await statistics.getOverview({ date_from, date_to })
      overview.value = overviewRes
      categoryStats.value = overviewRes.top_categories || []
      projectStats.value = overviewRes.top_projects || []
    } catch (e) {
      console.error('获取概览失败', e)
    }
    
    // 分类统计
    try {
      const catRes = await statistics.getCategories({ date_from, date_to })
      categoryStats.value = catRes.categories || []
    } catch (e) {
      console.error('获取分类统计失败', e)
    }
    
    // 项目统计
    try {
      const projRes = await statistics.getProjects({ date_from, date_to })
      projectStats.value = projRes.projects || []
    } catch (e) {
      console.error('获取项目统计失败', e)
    }
    
    // 月度趋势
    await fetchMonthlyTrend(date_from, date_to)
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

async function fetchMonthlyTrend(date_from, date_to) {
  try {
    const start = new Date(date_from || `${thisYear}-01-01`)
    const end = new Date(date_to || `${thisYear}-12-31`)
    const stats = []
    
    let current = new Date(start)
    while (current <= end) {
      const year = current.getFullYear()
      const month = current.getMonth() + 1
      
      try {
        const res = await statistics.getMonthly(year, month)
        stats.push(res)
      } catch (e) {
        stats.push({
          year,
          month,
          total_income: 0,
          total_expense: 0,
          balance: 0
        })
      }
      
      current.setMonth(current.getMonth() + 1)
    }
    
    monthlyStats.value = stats.reverse()
  } catch (e) {
    console.error('获取月度趋势失败', e)
  }
}
</script>

<style scoped>
.statistics-page {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.overview-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  border: none;
}

.stat-card.income-card {
  background: linear-gradient(135deg, #67c23a15, #67c23a08);
}

.stat-card.expense-card {
  background: linear-gradient(135deg, #f56c6c15, #f56c6c08);
}

.stat-card.balance-card {
  background: linear-gradient(135deg, #409eff15, #409eff08);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-content .el-icon {
  font-size: 48px;
  color: var(--el-color-primary);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.detail-card,
.trend-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: bold;
}

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}
</style>
