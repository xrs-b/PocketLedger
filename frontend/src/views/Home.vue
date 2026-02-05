<template>
  <div class="home-page">
    <!-- 欢迎语 -->
    <div class="welcome-section">
      <h2>你好，{{ authStore.user?.username || '用户' }}！</h2>
      <p class="date">{{ today }}</p>
    </div>
    
    <!-- 今日统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card income" shadow="hover">
          <div class="stat-label">今日收入</div>
          <div class="stat-value">¥{{ todayIncome.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card expense" shadow="hover">
          <div class="stat-label">今日支出</div>
          <div class="stat-value">¥{{ todayExpense.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card balance" shadow="hover">
          <div class="stat-label">今日结余</div>
          <div class="stat-value">¥{{ (todayIncome - todayExpense).toFixed(2) }}</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速记账 -->
    <el-card class="quick-actions">
      <template #header>
        <h3>快速记账</h3>
      </template>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-button
            type="success"
            size="large"
            class="action-btn"
            @click="$router.push('/records/add?type=income')"
          >
            <el-icon><Plus /></el-icon>
            记收入
          </el-button>
        </el-col>
        <el-col :span="12">
          <el-button
            type="warning"
            size="large"
            class="action-btn"
            @click="$router.push('/records/add?type=expense')"
          >
            <el-icon><Minus /></el-icon>
            记支出
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 最近记录 -->
    <el-card class="recent-records">
      <template #header>
        <div class="card-header">
          <h3>最近记录</h3>
          <el-link type="primary" @click="$router.push('/records')">
            查看全部
          </el-link>
        </div>
      </template>
      
      <div v-if="recentRecords.length === 0" class="empty-state">
        <el-empty description="暂无记账记录" />
      </div>
      
      <el-table v-else :data="recentRecords" style="width: 100%">
        <el-table-column prop="date" label="日期" width="100">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="category.name" label="分类" width="100" />
        <el-table-column prop="description" label="备注" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            <span :class="row.type === 'income' ? 'text-success' : 'text-danger'">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ row.amount.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Plus, Minus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})

const todayIncome = ref(0)
const todayExpense = ref(0)
const recentRecords = ref([])

onMounted(() => {
  fetchTodayStats()
  fetchRecentRecords()
})

async function fetchTodayStats() {
  try {
    // TODO: 调用 API 获取今日统计
    // const response = await client.get('/statistics/daily')
    // todayIncome.value = response.income
    // todayExpense.value = response.expense
  } catch (error) {
    console.error('获取今日统计失败:', error)
  }
}

async function fetchRecentRecords() {
  try {
    // TODO: 调用 API 获取最近记录
    // const response = await client.get('/records?limit=5')
    // recentRecords.value = response.records
  } catch (error) {
    console.error('获取最近记录失败:', error)
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.home-page {
  padding: 20px;
}

.welcome-section {
  margin-bottom: 20px;
}

.welcome-section h2 {
  margin: 0;
  font-size: 24px;
}

.date {
  color: #666;
  margin: 8px 0 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  border-radius: 8px;
}

.stat-card.income {
  border-left: 4px solid #67c23a;
}

.stat-card.expense {
  border-left: 4px solid #f56c6c;
}

.stat-card.balance {
  border-left: 4px solid #409eff;
}

.stat-label {
  color: #999;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.quick-actions,
.recent-records {
  margin-bottom: 20px;
  border-radius: 8px;
}

.action-btn {
  width: 100%;
  height: 60px;
  font-size: 18px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

.empty-state {
  padding: 40px 0;
}
</style>
