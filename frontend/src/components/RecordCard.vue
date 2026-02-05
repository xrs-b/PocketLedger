<template>
  <el-card class="record-card" shadow="hover">
    <div class="card-content">
      <div class="card-left">
        <el-avatar :size="40" :style="{ background: categoryColor }">
          <el-icon><component :is="categoryIcon" /></el-icon>
        </el-avatar>
        <div class="card-info">
          <div class="category-name">{{ record.category?.name || '未分类' }}</div>
          <div class="record-date">{{ formatDate(record.date) }}</div>
          <div v-if="record.description" class="record-desc">
            {{ record.description }}
          </div>
        </div>
      </div>
      
      <div class="card-right">
        <div :class="['amount', record.type === 'income' ? 'text-success' : 'text-danger']">
          {{ record.type === 'income' ? '+' : '-' }}¥{{ record.amount.toFixed(2) }}
        </div>
        
        <div v-if="record.project" class="project-tag">
          {{ record.project.name }}
        </div>
        
        <div class="card-actions">
          <el-button type="primary" link size="small" @click="$emit('edit', record)">
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button type="danger" link size="small" @click="$emit('delete', record)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-if="showDetails && (record.per_person || record.people_count)" class="card-details">
      <el-divider />
      <div class="detail-row">
        <span>人数：{{ record.people_count || 1 }} 人</span>
        <span>人均：¥{{ (record.per_person || record.amount).toFixed(2) }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Edit, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  record: {
    type: Object,
    required: true
  },
  showDetails: {
    type: Boolean,
    default: true
  }
})

defineEmits(['edit', 'delete'])

const categoryColor = computed(() => {
  const colors = {
    income: '#67c23a',
    expense: '#f56c6c',
    餐饮: '#e6a23c',
    交通: '#409eff',
    娱乐: '#909399',
    购物: '#eb2f96',
    居住: '#722ed1',
    医疗: '#13c2c2',
    教育: '#fa8c16',
    人情: '#b88230'
  }
  return colors[props.record.category?.name] || colors[props.record.type] || '#909399'
})

const categoryIcon = computed(() => {
  const icons = {
    餐饮: 'Food',
    交通: 'Van',
    娱乐: 'VideoPlay',
    购物: 'ShoppingCart',
    居住: 'House',
    医疗: 'FirstAid',
    教育: 'Reading',
    人情: 'Gift',
    工资: 'Money',
    奖金: 'Trophy',
    投资: 'TrendCharts',
    其他: 'More'
  }
  return icons[props.record.category?.name] || 'Wallet'
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()
  
  if (isToday) {
    return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.record-card {
  margin-bottom: 12px;
  border-radius: 8px;
  transition: all 0.3s;
}

.record-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.category-name {
  font-weight: 500;
  font-size: 15px;
}

.record-date {
  font-size: 12px;
  color: #909399;
}

.record-desc {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.amount {
  font-size: 18px;
  font-weight: bold;
}

.project-tag {
  font-size: 12px;
  color: #409eff;
  background: #ecf5ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.card-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.card-details {
  margin-top: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}
</style>
