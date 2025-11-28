<template>
  <div class="plan-management">
    <div class="header">
      <h1>套餐管理</h1>
      <el-button type="primary" @click="handleCreatePlan">
        <el-icon><Plus /></el-icon>
        新增套餐
      </el-button>
    </div>

    <el-card>
      <el-table :data="plans" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="套餐代码" min-width="120" />
        <el-table-column prop="display_name" label="套餐名称" min-width="150" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">¥{{ parseFloat(row.price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="original_price" label="原价" width="100">
          <template #default="{ row }">
            <span v-if="row.original_price">¥{{ parseFloat(row.original_price).toFixed(2) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration_days" label="时长(天)" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEditPlan(row)">编辑</el-button>
            <el-popconfirm
              title="确定删除此套餐吗？"
              @confirm="handleDeletePlan(row.id)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingPlan ? '编辑套餐' : '新增套餐'"
      width="500px"
    >
      <el-form
        :model="formData"
        :rules="formRules"
        label-width="100px"
        ref="formRef"
      >
        <el-form-item label="套餐代码" prop="name">
          <el-input
            v-model="formData.name"
            :disabled="!!editingPlan"
            placeholder="如：monthly, yearly"
          />
        </el-form-item>
        <el-form-item label="套餐名称" prop="display_name">
          <el-input v-model="formData.display_name" placeholder="如：月度套餐" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            rows="3"
            placeholder="套餐描述信息"
          />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number
            v-model="formData.price"
            :precision="2"
            :min="0"
            placeholder="0.00"
          />
        </el-form-item>
        <el-form-item label="原价" prop="original_price">
          <el-input-number
            v-model="formData.original_price"
            :precision="2"
            :min="0"
            placeholder="不填则不显示原价"
          />
        </el-form-item>
        <el-form-item label="时长(天)" prop="duration_days">
          <el-input-number
            v-model="formData.duration_days"
            :min="1"
            placeholder="30"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePlan">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

interface Plan {
  id: number
  name: string
  display_name: string
  description: string
  price: number
  original_price?: number
  duration_days: number
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

interface FormData {
  name: string
  display_name: string
  description: string
  price: number
  original_price?: number
  duration_days: number
  is_active: boolean
  sort_order: number
}

const plans = ref<Plan[]>([])
const dialogVisible = ref(false)
const editingPlan = ref<Plan | null>(null)
const formRef = ref()
const formData = ref<FormData>({
  name: '',
  display_name: '',
  description: '',
  price: 0,
  original_price: undefined,
  duration_days: 30,
  is_active: true,
  sort_order: 0,
})

const formRules = {
  name: [{ required: true, message: '请输入套餐代码', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入套餐名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  duration_days: [{ required: true, message: '请输入时长', trigger: 'blur' }],
}

// TODO: 这里需要实现实际的 API 调用
// 目前使用模拟数据
const loadPlans = async () => {
  try {
    // const response = await fetch('/api/v1/admin/plans')
    // const data = await response.json()
    // plans.value = data
    // 模拟数据
    plans.value = [
      {
        id: 1,
        name: 'monthly',
        display_name: '月度套餐',
        description: '月度订阅，享受所有报表功能',
        price: 99,
        original_price: 129,
        duration_days: 30,
        is_active: true,
        sort_order: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        name: 'quarterly',
        display_name: '季度套餐',
        description: '季度订阅，性价比更优',
        price: 249,
        original_price: 349,
        duration_days: 90,
        is_active: true,
        sort_order: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 3,
        name: 'yearly',
        display_name: '年度套餐',
        description: '年度订阅，折扣力度最大',
        price: 699,
        original_price: 1000,
        duration_days: 365,
        is_active: true,
        sort_order: 3,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]
  } catch (error) {
    ElMessage.error('加载套餐列表失败')
  }
}

const handleCreatePlan = () => {
  editingPlan.value = null
  formData.value = {
    name: '',
    display_name: '',
    description: '',
    price: 0,
    original_price: undefined,
    duration_days: 30,
    is_active: true,
    sort_order: 0,
  }
  dialogVisible.value = true
}

const handleEditPlan = (plan: Plan) => {
  editingPlan.value = plan
  formData.value = { ...plan }
  dialogVisible.value = true
}

const handleSavePlan = async () => {
  if (!formRef.value) return

  await formRef.value.validate()
  try {
    if (editingPlan.value) {
      // TODO: 调用编辑 API
      // await fetch(`/api/v1/admin/plans/${editingPlan.value.id}`, {
      //   method: 'PUT',
      //   body: JSON.stringify(formData.value),
      // })
      ElMessage.success('套餐更新成功')
    } else {
      // TODO: 调用创建 API
      // await fetch('/api/v1/admin/plans', {
      //   method: 'POST',
      //   body: JSON.stringify(formData.value),
      // })
      ElMessage.success('套餐创建成功')
    }
    dialogVisible.value = false
    await loadPlans()
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  }
}

const handleDeletePlan = async (planId: number) => {
  try {
    // TODO: 调用删除 API
    // await fetch(`/api/v1/admin/plans/${planId}`, {
    //   method: 'DELETE',
    // })
    ElMessage.success('套餐删除成功')
    await loadPlans()
  } catch (error) {
    ElMessage.error('删除失败，请重试')
  }
}

onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.plan-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

:deep(.el-dialog__title) {
  font-size: 18px;
}
</style>
