<template>
  <div class="record-detail-page">
    <el-page-header @back="$router.back()" style="margin-bottom: 20px">
      <template #content>
        <span class="page-title">记账详情</span>
      </template>
    </el-page-header>
    
    <el-card v-if="record" class="detail-card">
      <!-- 金额显示 -->
      <div class="amount-section">
        <div :class="['amount', record.type === 'income' ? 'text-success' : 'text-danger']">
          {{ record.type === 'income' ? '+' : '-' }}¥{{ record.amount.toFixed(2) }}
        </div>
        <div class="record-type">
          <CategoryTag :name="record.category?.name || '未分类'" :type="record.type" />
        </div>
      </div>
      
      <el-divider />
      
      <!-- 详细信息 -->
      <el-descriptions :column="1" border>
        <el-descriptions-item label="日期">
          {{ formatDate(record.date) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="分类">
          {{ record.category?.name || '未分类' }}
          <span v-if="record.category?.parent" style="color: #909399">
            / {{ record.category.parent.name }}
          </span>
        </el-descriptions-item>
        
        <el-descriptions-item label="备注" v-if="record.description">
          {{ record.description }}
        </el-descriptions-item>
        
        <el-descriptions-item label="关联项目" v-if="record.project">
          <el-tag type="success">{{ record.project.name }}</el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="记账人">
          {{ record.user?.name || record.user?.username || '未知' }}
        </el-descriptions-item>
        
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(record.created_at) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(record.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
      
      <!-- AA 制信息 -->
      <template v-if="record.people_count && record.people_count > 1">
        <el-divider />
        <div class="aa-section">
          <h4>AA 分摊</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="人数">
              {{ record.people_count }} 人
            </el-descriptions-item>
            <el-descriptions-item label="人均">
              ¥{{ (record.per_person || 0).toFixed(2) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </template>
      
      <!-- 操作按钮 -->
      <div class="actions-section">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
        <el-button type="danger" @click="handleDelete">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
    </el-card>
    
    <el-skeleton v-else :rows="6" animated />
    
    <!-- 删除确认 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="300px"
      center
    >
      <span>确定要删除这条记账记录吗？此操作不可恢复。</span>
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { records } from '@/api/records'
import CategoryTag from '@/components/CategoryTag.vue'

const router = useRouter()
const route = useRoute()
const record = ref(null)
const loading = ref(true)
const deleteDialogVisible = ref(false)
const deleting = ref(false)

onMounted(() => {
  fetchRecord()
})

async function fetchRecord() {
  loading.value = true
  try {
    const id = route.params.id
    record.value = await records.get(id)
  } catch (error) {
    ElMessage.error('获取记录详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

function handleEdit() {
  router.push(`/records/${route.params.id}/edit`)
}

function handleDelete() {
  deleteDialogVisible.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await records.delete(route.params.id)
    ElMessage.success('删除成功')
    router.push('/records')
  } catch (error) {
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
    deleteDialogVisible.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.record-detail-page {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  font-weight: 500;
  font-size: 18px;
}

.detail-card {
  border-radius: 8px;
}

.amount-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.amount {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 12px;
}

.record-type {
  margin-top: 8px;
}

.aa-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.actions-section {
  display: flex;
  justify-content: center;
  gap: 20px;
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
</style>
