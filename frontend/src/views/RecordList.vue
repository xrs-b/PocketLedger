<template>
  <div class="record-list-page">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="分类">
          <el-select
            v-model="filters.categoryId"
            placeholder="全部分类"
            clearable
          >
            <el-option label="餐饮" value="1" />
            <el-option label="交通" value="2" />
            <!-- 更多分类 -->
          </el-select>
        </el-form-item>
        
        <el-form-item label="类型">
          <el-radio-group v-model="filters.type">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="income">收入</el-radio-button>
            <el-radio-button label="expense">支出</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <h3>记账记录</h3>
          <el-button type="primary" @click="$router.push('/records/add')">
            新增记账
          </el-button>
        </div>
      </template>
      
      <el-table :data="records" stripe style="width: 100%">
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="category.name" label="分类" width="100" />
        
        <el-table-column prop="description" label="备注" />
        
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span :class="row.type === 'income' ? 'text-success' : 'text-danger'">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ row.amount.toFixed(2) }}
            </span>
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
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchRecords"
          @current-change="fetchRecords"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const records = ref([])
const loading = ref(false)

const filters = reactive({
  dateRange: [],
  categoryId: '',
  type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

onMounted(() => {
  fetchRecords()
})

async function fetchRecords() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    if (filters.dateRange?.length === 2) {
      params.date_from = filters.dateRange[0]
      params.date_to = filters.dateRange[1]
    }
    
    if (filters.categoryId) {
      params.category_id = filters.categoryId
    }
    
    if (filters.type) {
      params.type = filters.type
    }
    
    const response = await client.get('/records', { params })
    records.value = response.records
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('获取记账记录失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchRecords()
}

function handleReset() {
  filters.dateRange = []
  filters.categoryId = ''
  filters.type = ''
  pagination.page = 1
  fetchRecords()
}

function handleEdit(record) {
  router.push(`/records/${record.id}/edit`)
}

async function handleDelete(record) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记账记录吗？',
      '确认删除',
      { type: 'warning' }
    )
    
    await client.delete(`/records/${record.id}`)
    ElMessage.success('删除成功')
    fetchRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.record-list-page {
  padding: 20px;
}

.filter-card,
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

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}
</style>
