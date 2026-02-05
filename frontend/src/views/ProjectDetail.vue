<template>
  <div class="project-detail-page">
    <el-page-header @back="$router.back()" style="margin-bottom: 20px">
      <template #content>
        <span class="page-title">{{ project?.name || '项目详情' }}</span>
      </template>
      <template #extra>
        <el-button type="primary" link @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
      </template>
    </el-page-header>
    
    <el-card v-if="project" class="detail-card">
      <!-- 项目状态 -->
      <div class="status-section">
        <el-tag :type="getStatusType(project.status)" size="large">
          {{ getStatusLabel(project.status) }}
        </el-tag>
      </div>
      
      <!-- 预算信息 -->
      <div class="budget-section">
        <div class="budget-amount">
          <span class="label">预算</span>
          <span class="value">¥{{ (project.budget || 0).toFixed(2) }}</span>
        </div>
        <div class="budget-spent">
          <span class="label">已花费</span>
          <span class="value" :class="spentClass">{{ spentText }}</span>
        </div>
        <div class="budget-usage">
          <el-progress 
            :percentage="Math.min(project.budget_usage || 0, 100)"
            :status="getBudgetStatus()"
            :stroke-width="12"
          />
          <span class="usage-text">{{ project.budget_usage?.toFixed(1) || 0 }}%</span>
        </div>
      </div>
      
      <el-divider />
      
      <!-- 项目信息 -->
      <el-descriptions :column="1" border>
        <el-descriptions-item label="项目名称">{{ project.name }}</el-descriptions-item>
        
        <el-descriptions-item label="描述" v-if="project.description">
          {{ project.description }}
        </el-descriptions-item>
        
        <el-descriptions-item label="时间范围">
          {{ project.start_date || '-' }} 至 {{ project.end_date || '-' }}
        </el-descriptions-item>
        
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(project.created_at) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(project.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
      
      <!-- 项目统计 -->
      <el-divider />
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value text-success">+¥{{ (projectStats.total_income || 0).toFixed(2) }}</div>
              <div class="stat-label">项目收入</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value text-danger">-¥{{ (projectStats.total_expense || 0).toFixed(2) }}</div>
              <div class="stat-label">项目支出</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div :class="['stat-value', projectStats.balance >= 0 ? 'text-success' : 'text-danger']">
                {{ projectStats.balance >= 0 ? '+' : '' }}¥{{ (projectStats.balance || 0).toFixed(2) }}
              </div>
              <div class="stat-label">项目结余</div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 关联记账记录 -->
      <el-divider />
      <div class="records-section">
        <div class="section-header">
          <h4>关联记账 ({{ projectRecords.length }})</h4>
          <el-button type="primary" link size="small" @click="$router.push(`/records/add?project_id=${project.id}`)">
            添加记账
          </el-button>
        </div>
        
        <div v-if="projectRecords.length > 0" class="records-list">
          <div v-for="record in projectRecords" :key="record.id" class="record-item">
            <div class="record-info">
              <CategoryTag :name="record.category?.name" :type="record.type" size="small" />
              <span class="record-date">{{ record.date }}</span>
            </div>
            <div :class="['record-amount', record.type === 'income' ? 'text-success' : 'text-danger']">
              {{ record.type === 'income' ? '+' : '-' }}¥{{ record.amount.toFixed(2) }}
            </div>
          </div>
        </div>
        
        <el-empty v-else description="暂无关联记账" :image-size="80">
          <el-button type="primary" size="small" @click="$router.push(`/records/add?project_id=${project.id}`)">
            添加第一条记账
          </el-button>
        </el-empty>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions-section">
        <el-button 
          v-if="project.status === 'active'"
          type="success" 
          @click="updateStatus('completed')"
        >
          标记为完成
        </el-button>
        <el-button 
          v-if="project.status !== 'archived'"
          type="info" 
          @click="updateStatus('archived')"
        >
          归档项目
        </el-button>
        <el-button type="danger" @click="handleDelete">
          删除项目
        </el-button>
      </div>
    </el-card>
    
    <el-skeleton v-else :rows="8" animated />
    
    <!-- 删除确认 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="300px"
      center
    >
      <span>确定要删除项目"{{ project?.name }}"吗？此操作不可恢复。</span>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleting">
          删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { projects } from '@/api/projects'
import CategoryTag from '@/components/CategoryTag.vue'

const router = useRouter()
const route = useRoute()
const project = ref(null)
const projectStats = ref({})
const projectRecords = ref([])
const loading = ref(true)
const deleteDialogVisible = ref(false)
const deleting = ref(false)

onMounted(() => {
  fetchProject()
})

async function fetchProject() {
  loading.value = true
  try {
    const id = route.params.id
    project.value = await projects.get(id)
    
    // 获取项目统计
    try {
      projectStats.value = await projects.getStats(id)
    } catch (e) {
      projectStats.value = {}
    }
    
    // 获取关联记账
    try {
      const res = await projects.getRecords(id)
      projectRecords.value = res.records || []
    } catch (e) {
      projectRecords.value = []
    }
  } catch (error) {
    ElMessage.error('获取项目详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

const spentClass = computed(() => {
  const usage = project.value?.budget_usage || 0
  if (usage >= 100) return 'text-danger'
  if (usage >= 80) return 'text-warning'
  return ''
})

const spentText = computed(() => {
  const spent = project.value?.spent || 0
  const budget = project.value?.budget || 0
  return `¥${spent.toFixed(2)} / ¥${budget.toFixed(2)}`
})

function handleEdit() {
  router.push(`/projects/${route.params.id}/edit`)
}

function handleDelete() {
  deleteDialogVisible.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await projects.delete(route.params.id)
    ElMessage.success('删除成功')
    router.push('/projects')
  } catch (error) {
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
    deleteDialogVisible.value = false
  }
}

async function updateStatus(status) {
  try {
    await projects.update(route.params.id, { status })
    ElMessage.success('状态更新成功')
    project.value.status = status
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

function getStatusLabel(status) {
  const labels = { active: '进行中', completed: '已完成', archived: '已归档' }
  return labels[status] || status
}

function getStatusType(status) {
  const types = { active: 'primary', completed: 'success', archived: 'info' }
  return types[status] || 'info'
}

function getBudgetStatus() {
  const usage = project.value?.budget_usage || 0
  if (usage >= 100) return 'exception'
  if (usage >= 80) return 'warning'
  return ''
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.project-detail-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-weight: 500;
  font-size: 18px;
}

.detail-card {
  border-radius: 8px;
}

.status-section {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.budget-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 20px;
}

.budget-amount,
.budget-spent {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.budget-amount .value {
  font-weight: bold;
  font-size: 20px;
}

.budget-spent .value {
  font-weight: 500;
  font-size: 18px;
}

.budget-usage {
  display: flex;
  align-items: center;
  gap: 12px;
}

.budget-usage .el-progress {
  flex: 1;
}

.usage-text {
  font-size: 14px;
  color: #909399;
  min-width: 45px;
}

.stats-section {
  padding: 10px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.records-section {
  margin-top: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h4 {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.record-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.record-date {
  font-size: 12px;
  color: #909399;
}

.record-amount {
  font-weight: 500;
}

.actions-section {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

.text-warning {
  color: #e6a23c;
}
</style>
