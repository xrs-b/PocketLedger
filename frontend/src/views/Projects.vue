<template>
  <div class="projects-page">
    <!-- 项目列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <h3>项目管理</h3>
          <div class="header-actions">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px">
              <el-option label="进行中" value="active" />
              <el-option label="已完成" value="completed" />
              <el-option label="已归档" value="archived" />
            </el-select>
            <el-button type="primary" @click="showCreateDialog">
              新建项目
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="projects" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="项目名称" width="180">
          <template #default="{ row }">
            <el-link type="primary" @click="viewProject(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        
        <el-table-column prop="budget" label="预算" width="120">
          <template #default="{ row }">
            ¥{{ (row.budget || 0).toFixed(2) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="spent" label="已花费" width="120">
          <template #default="{ row }">
            <span :class="getSpentClass(row)">
              ¥{{ (row.spent || 0).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="budget_usage" label="预算使用率" width="150">
          <template #default="{ row }">
            <el-progress 
              :percentage="Math.min(row.budget_usage || 0, 100)"
              :status="getBudgetStatus(row)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="date_range" label="时间范围" width="200">
          <template #default="{ row }">
            {{ row.start_date || '-' }} 至 {{ row.end_date || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewProject(row)">
              查看
            </el-button>
            <el-button type="primary" link @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchProjects"
          @current-change="fetchProjects"
        />
      </div>
    </el-card>

    <!-- 项目详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="项目详情" size="50%">
      <template v-if="currentProject">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ currentProject.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentProject.status)">
              {{ getStatusLabel(currentProject.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预算">
            ¥{{ (currentProject.budget || 0).toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item label="已花费">
            <span :class="getSpentClass(currentProject)">
              ¥{{ (currentProject.spent || 0).toFixed(2) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ currentProject.start_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ currentProject.end_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentProject.description || '无' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <h4>预算使用情况</h4>
        <el-progress 
          :percentage="Math.min(currentProject.budget_usage || 0, 100)"
          :status="getBudgetStatus(currentProject)"
          :stroke-width="20"
        />
        <p style="margin-top: 8px; color: #909399">
          已花费 ¥{{ (currentProject.spent || 0).toFixed(2) }} / 预算 ¥{{ (currentProject.budget || 0).toFixed(2) }}
        </p>
        
        <el-divider />
        
        <div class="drawer-actions">
          <el-button type="primary" @click="handleEdit(currentProject)">编辑项目</el-button>
          <el-button 
            v-if="currentProject.status === 'active'"
            type="success" 
            @click="updateStatus(currentProject, 'completed')"
          >
            标记为完成
          </el-button>
          <el-button 
            v-if="currentProject.status !== 'archived'"
            type="info" 
            @click="updateStatus(currentProject, 'archived')"
          >
            归档项目
          </el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑项目' : '新建项目'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：2024年装修" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="项目描述..."
          />
        </el-form-item>
        
        <el-form-item label="预算金额" prop="budget">
          <el-input-number
            v-model="formData.budget"
            :min="0"
            :precision="2"
            :step="1000"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="formData.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projects as projectApi } from '@/api/projects'

const projects = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const drawerVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const currentProject = ref(null)
const formRef = ref(null)

const statusFilter = ref('')
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  name: '',
  description: '',
  budget: 0,
  dateRange: []
})

const formRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  budget: [{ required: true, message: '请输入预算金额', trigger: 'blur' }]
}

watch(statusFilter, () => {
  pagination.page = 1
  fetchProjects()
})

onMounted(() => {
  fetchProjects()
})

async function fetchProjects() {
  loading.value = true
  try {
    const response = await projectApi.list({
      page: pagination.page,
      page_size: pagination.pageSize,
      status: statusFilter.value || undefined
    })
    projects.value = response.projects
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false
  editingId.value = null
  formData.name = ''
  formData.description = ''
  formData.budget = 0
  formData.dateRange = []
  dialogVisible.value = true
}

function handleEdit(project) {
  isEdit.value = true
  editingId.value = project.id
  formData.name = project.name
  formData.description = project.description || ''
  formData.budget = project.budget || 0
  formData.dateRange = project.start_date && project.end_date 
    ? [project.start_date, project.end_date] 
    : []
  dialogVisible.value = true
}

function viewProject(project) {
  currentProject.value = project
  drawerVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    
    submitLoading.value = true
    const data = {
      name: formData.name,
      description: formData.description,
      budget: formData.budget
    }
    
    if (formData.dateRange?.length === 2) {
      data.start_date = formData.dateRange[0]
      data.end_date = formData.dateRange[1]
    }
    
    if (isEdit.value) {
      await projectApi.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await projectApi.create(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(project) {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await projectApi.delete(project.id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function updateStatus(project, status) {
  try {
    await projectApi.update(project.id, { status })
    ElMessage.success('状态更新成功')
    drawerVisible.value = false
    fetchProjects()
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

function getStatusLabel(status) {
  const labels = {
    active: '进行中',
    completed: '已完成',
    archived: '已归档'
  }
  return labels[status] || status
}

function getStatusType(status) {
  const types = {
    active: 'primary',
    completed: 'success',
    archived: 'info'
  }
  return types[status] || 'info'
}

function getSpentClass(project) {
  const usage = project.budget_usage || 0
  if (usage >= 100) return 'text-danger'
  if (usage >= 80) return 'text-warning'
  return ''
}

function getBudgetStatus(project) {
  const usage = project.budget_usage || 0
  if (usage >= 100) return 'exception'
  if (usage >= 80) return 'warning'
  return ''
}
</script>

<style scoped>
.projects-page {
  padding: 20px;
}

.table-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.drawer-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

.text-warning {
  color: #e6a23c;
  font-weight: bold;
}
</style>
