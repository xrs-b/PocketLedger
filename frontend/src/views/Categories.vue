<template>
  <div class="categories-page">
    <!-- 分类列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <h3>分类管理</h3>
          <div class="header-actions">
            <el-radio-group v-model="typeFilter" @change="fetchCategories">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="income">收入</el-radio-button>
              <el-radio-button label="expense">支出</el-radio-button>
            </el-radio-group>
            <el-button type="primary" @click="showCreateDialog">
              新增分类
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="categories" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="分类名称" width="150" />
        
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="icon" label="图标" width="100">
          <template #default="{ row }">
            <el-icon><component :is="getIcon(row.icon)" /></el-icon>
          </template>
        </el-table-column>
        
        <el-table-column prop="parent_name" label="上级分类" width="120">
          <template #default="{ row }">
            {{ row.parent?.name || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="sort_order" label="排序" width="80" />
        
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
          @size-change="fetchCategories"
          @current-change="fetchCategories"
        />
      </div>
    </el-card>

    <!-- 创建/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '新增分类'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：餐饮" />
        </el-form-item>
        
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="formData.type">
            <el-radio-button label="income">收入</el-radio-button>
            <el-radio-button label="expense">支出</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="上级分类">
          <el-select
            v-model="formData.parent_id"
            placeholder="选择上级分类（留空为一级分类）"
            clearable
          >
            <el-option
              v-for="cat in parentCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="排序">
          <el-input-number v-model="formData.sort_order" :min="0" :step="1" />
        </el-form-item>
        
        <el-form-item label="图标">
          <el-input v-model="formData.icon" placeholder="Element Plus 图标名" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categories as categoryApi } from '@/api/categories'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const categories = ref([])
const parentCategories = ref([])
const typeFilter = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const formData = reactive({
  name: '',
  type: 'expense',
  parent_id: null,
  sort_order: 0,
  icon: ''
})

const formRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }]
}

onMounted(() => {
  fetchCategories()
})

async function fetchCategories() {
  loading.value = true
  try {
    const response = await categoryApi.list({
      page: pagination.page,
      page_size: pagination.pageSize,
      type: typeFilter.value || undefined
    })
    categories.value = response.categories
    pagination.total = response.total
    
    // 获取一级分类作为上级选项
    const parentRes = await categoryApi.list({ page_size: 100, parent_id: 'null' })
    parentCategories.value = parentRes.categories || []
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false
  editingId.value = null
  formData.name = ''
  formData.type = 'expense'
  formData.parent_id = null
  formData.sort_order = 0
  formData.icon = ''
  dialogVisible.value = true
}

function handleEdit(category) {
  isEdit.value = true
  editingId.value = category.id
  formData.name = category.name
  formData.type = category.type
  formData.parent_id = category.parent_id
  formData.sort_order = category.sort_order || 0
  formData.icon = category.icon || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    
    submitLoading.value = true
    const data = {
      name: formData.name,
      type: formData.type,
      sort_order: formData.sort_order
    }
    
    if (formData.parent_id) {
      data.parent_id = formData.parent_id
    }
    
    if (formData.icon) {
      data.icon = formData.icon
    }
    
    if (isEdit.value) {
      await categoryApi.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await categoryApi.create(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(category) {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${category.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await categoryApi.delete(category.id)
    ElMessage.success('删除成功')
    fetchCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getIcon(iconName) {
  return iconName || 'Wallet'
}
</script>

<style scoped>
.categories-page {
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
</style>
