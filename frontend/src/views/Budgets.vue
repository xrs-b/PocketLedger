<template>
  <div class="budgets-page">
    <!-- 超支提醒 -->
    <el-card v-if="alerts.length > 0" class="alert-card">
      <template #header>
        <div class="alert-header">
          <el-icon><Warning /></el-icon>
          <span>预算超支提醒</span>
        </div>
      </template>
      <el-alert
        v-for="alert in alerts"
        :key="alert.budget_id"
        :title="alert.message"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 8px"
      />
    </el-card>

    <!-- 预算列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <h3>预算管理</h3>
          <el-button type="primary" @click="showCreateDialog">
            新增预算
          </el-button>
        </div>
      </template>
      
      <el-table :data="budgets" stripe style="width: 100%">
        <el-table-column prop="name" label="预算名称" width="150" />
        
        <el-table-column prop="category.name" label="分类" width="100">
          <template #default="{ row }">
            {{ row.category?.name || '全部分类' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="amount" label="预算金额" width="120">
          <template #default="{ row }">
            ¥{{ row.amount.toFixed(2) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="spent" label="已花费" width="120">
          <template #default="{ row }">
            <span :class="getSpentClass(row)">
              ¥{{ (row.spent || 0).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="percentage" label="使用率" width="150">
          <template #default="{ row }">
            <el-progress 
              :percentage="Math.min(row.percentage || 0, 100)"
              :status="getProgressStatus(row.percentage)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="period_type" label="周期" width="100">
          <template #default="{ row }">
            <el-tag>{{ getPeriodLabel(row.period_type) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="date_range" label="时间范围">
          <template #default="{ row }">
            {{ row.start_date }} 至 {{ row.end_date }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
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
          @size-change="fetchBudgets"
          @current-change="fetchBudgets"
        />
      </div>
    </el-card>

    <!-- 创建/编辑预算对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑预算' : '新增预算'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="预算名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：1月餐饮预算" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category_id">
          <el-select
            v-model="formData.category_id"
            placeholder="选择分类（留空为全部）"
            clearable
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="预算金额" prop="amount">
          <el-input-number
            v-model="formData.amount"
            :min="0"
            :precision="2"
            :step="100"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="周期类型" prop="period_type">
          <el-radio-group v-model="formData.period_type">
            <el-radio-button label="monthly">月度</el-radio-button>
            <el-radio-button label="yearly">年度</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="时间范围" prop="dateRange">
          <el-date-picker
            v-model="formData.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :disabled="formData.period_type !== 'custom'"
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
import { ref, reactive, onMounted } from 'vue'
import { Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { budgets as budgetApi } from '@/api/budgets'
import { categories as categoryApi } from '@/api/categories'

const budgets = ref([])
const categories = ref([])
const alerts = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  name: '',
  category_id: null,
  amount: 0,
  period_type: 'monthly',
  dateRange: []
})

const formRules = {
  name: [{ required: true, message: '请输入预算名称', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入预算金额', trigger: 'blur' }],
  period_type: [{ required: true, message: '请选择周期类型', trigger: 'change' }]
}

onMounted(() => {
  fetchBudgets()
  fetchAlerts()
  fetchCategories()
})

async function fetchBudgets() {
  loading.value = true
  try {
    const response = await budgetApi.list({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    budgets.value = response.budgets
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('获取预算列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchAlerts() {
  try {
    const response = await budgetApi.getAlerts()
    alerts.value = response.alerts || []
  } catch (error) {
    console.error('获取超支提醒失败', error)
  }
}

async function fetchCategories() {
  try {
    const response = await categoryApi.list({ page_size: 100 })
    categories.value = response.categories || []
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

function showCreateDialog() {
  isEdit.value = false
  editingId.value = null
  formData.name = ''
  formData.category_id = null
  formData.amount = 0
  formData.period_type = 'monthly'
  formData.dateRange = []
  dialogVisible.value = true
}

function handleEdit(budget) {
  isEdit.value = true
  editingId.value = budget.id
  formData.name = budget.name
  formData.category_id = budget.category_id
  formData.amount = budget.amount
  formData.period_type = budget.period_type
  formData.dateRange = [budget.start_date, budget.end_date]
  dialogVisible.value = true
}

async function handleSubmit() {
  try await formRef.value.validate()
  
  submitLoading.value = true
  const data = {
    name: formData.name,
    amount: formData.amount,
    period_type: formData.period_type,
    category_id: formData.category_id
  }
  
  if (formData.period_type === 'custom' && formData.dateRange?.length === 2) {
    data.start_date = formData.dateRange[0]
    data.end_date = formData.dateRange[1]
  }
  
  if (isEdit.value) {
    await budgetApi.update(editingId.value, data)
    ElMessage.success('更新成功')
  } else {
    await budgetApi.create(data)
    ElMessage.success('创建成功')
  }
  
  dialogVisible.value = false
  fetchBudgets()
  fetchAlerts()
} catch (error) {
  if (error !== 'cancel') {
    ElMessage.error('操作失败')
  }
} finally {
  submitLoading.value = false
}

async function handleDelete(budget) {
  try {
    await ElMessageBox.confirm(
      `确定要删除预算"${budget.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await budgetApi.delete(budget.id)
    ElMessage.success('删除成功')
    fetchBudgets()
    fetchAlerts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getPeriodLabel(type) {
  const labels = {
    monthly: '月度',
    yearly: '年度',
    custom: '自定义'
  }
  return labels[type] || type
}

function getSpentClass(budget) {
  const percentage = budget.percentage || 0
  if (percentage >= 100) return 'text-danger'
  if (percentage >= 80) return 'text-warning'
  return ''
}

function getProgressStatus(percentage) {
  if (percentage >= 100) return 'exception'
  if (percentage >= 80) return 'warning'
  return ''
}
</script>

<style scoped>
.budgets-page {
  padding: 20px;
}

.alert-card {
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid #e6a23c;
  background: #fdf6ec;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e6a23c;
  font-weight: bold;
}

.table-card {
  margin-bottom: 20px;
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

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

.text-warning {
  color: #e6a23c;
}
</style>
