<template>
  <div class="subscription-management">
    <div class="header">
      <h1>订阅管理</h1>
      <el-button type="primary" @click="handleCreateSubscription">
        <el-icon><Plus /></el-icon>
        新增订阅
      </el-button>
    </div>

    <!-- 搜索和过滤 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索用户名或邮箱"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="8">
          <el-select
            v-model="filterForm.status"
            placeholder="订阅状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="活跃" value="active" />
            <el-option label="过期" value="expired" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 订阅列表 -->
    <el-card>
      <el-table :data="subscriptions" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="用户" min-width="150">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="username">{{ row.user_id }}</span>
              <!-- 这里应该显示用户名或邮箱，需要关联用户数据 -->
            </div>
          </template>
        </el-table-column>
        <el-table-column label="套餐" min-width="120">
          <template #default="{ row }">
            <span v-if="row.plan">{{ row.plan.display_name }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="150">
          <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
        </el-table-column>
        <el-table-column label="过期时间" width="150">
          <template #default="{ row }">{{ formatDate(row.end_date) }}</template>
        </el-table-column>
        <el-table-column label="剩余天数" width="100">
          <template #default="{ row }">
            <el-tag :type="row.days_remaining > 0 ? 'success' : 'danger'">
              {{ row.days_remaining }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewDetails(row)">详情</el-button>
            <el-button link type="primary" size="small" @click="handleExtendSubscription(row)">延期</el-button>
            <el-button link type="warning" size="small" @click="handleEditSubscription(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleCancelSubscription(row.id)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 查看详情抽屉 -->
    <el-drawer
      v-model="detailsDrawerVisible"
      title="订阅详情"
      size="40%"
    >
      <div v-if="selectedSubscription" class="details-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户ID">
            {{ selectedSubscription.user_id }}
          </el-descriptions-item>
          <el-descriptions-item label="套餐">
            <span v-if="selectedSubscription.plan">{{ selectedSubscription.plan.display_name }}</span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDate(selectedSubscription.start_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="过期时间">
            {{ formatDate(selectedSubscription.end_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="剩余天数">
            {{ selectedSubscription.days_remaining }}
          </el-descriptions-item>
          <el-descriptions-item label="支付金额">
            ¥{{ parseFloat(selectedSubscription.amount_paid).toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">
            {{ selectedSubscription.payment_method || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="交易ID">
            {{ selectedSubscription.transaction_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedSubscription.status)">
              {{ selectedSubscription.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注">
            {{ selectedSubscription.notes || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="logs-section">
          <h3>变更历史</h3>
          <el-timeline>
            <el-timeline-item
              v-for="log in subscriptionLogs"
              :key="log.id"
              :timestamp="formatDate(log.created_at)"
              placement="top"
            >
              <div>
                <span class="log-action">{{ log.action }}</span>
                <span v-if="log.old_end_date && log.new_end_date" class="log-detail">
                  从 {{ formatDate(log.old_end_date) }} 延期至 {{ formatDate(log.new_end_date) }}
                </span>
                <span v-else class="log-detail">{{ log.details }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-drawer>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingSubscription ? '编辑订阅' : '新增订阅'"
      width="500px"
    >
      <el-form
        :model="formData"
        :rules="formRules"
        label-width="100px"
        ref="formRef"
      >
        <el-form-item label="用户ID" prop="user_id">
          <el-input-number v-model="formData.user_id" :min="1" />
        </el-form-item>
        <el-form-item label="套餐" prop="plan_id">
          <el-select v-model="formData.plan_id" placeholder="选择套餐">
            <el-option
              v-for="plan in plansOptions"
              :key="plan.id"
              :label="plan.display_name"
              :value="plan.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_date">
          <el-date-picker
            v-model="formData.start_date"
            type="datetime"
            placeholder="选择开始时间"
          />
        </el-form-item>
        <el-form-item label="过期时间" prop="end_date">
          <el-date-picker
            v-model="formData.end_date"
            type="datetime"
            placeholder="选择过期时间"
          />
        </el-form-item>
        <el-form-item label="支付金额" prop="amount_paid">
          <el-input-number
            v-model="formData.amount_paid"
            :precision="2"
            :min="0"
          />
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="formData.payment_method" placeholder="选择支付方式" clearable>
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="手动" value="manual" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveSubscription">保存</el-button>
      </template>
    </el-dialog>

    <!-- 延期对话框 -->
    <el-dialog
      v-model="extendDialogVisible"
      title="延期订阅"
      width="400px"
    >
      <el-form :model="extendForm" label-width="80px">
        <el-form-item label="延期天数">
          <el-input-number v-model="extendForm.days" :min="1" placeholder="30" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="extendDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmExtend">确认延期</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

interface Subscription {
  id: number
  user_id: number
  plan_id?: number
  plan?: any
  start_date: string
  end_date: string
  amount_paid: number
  payment_method?: string
  transaction_id?: string
  status: string
  notes?: string
  created_at: string
  updated_at: string
  is_valid: boolean
  days_remaining: number
}

interface SubscriptionLog {
  id: number
  subscription_id: number
  user_id?: number
  action: string
  old_end_date?: string
  new_end_date?: string
  details?: string
  performed_by?: number
  created_at: string
}

interface FormData {
  user_id: number
  plan_id?: number
  start_date: string
  end_date: string
  amount_paid: number
  payment_method?: string
  status: string
}

const subscriptions = ref<Subscription[]>([])
const plansOptions = ref<any[]>([])
const selectedSubscription = ref<Subscription | null>(null)
const subscriptionLogs = ref<SubscriptionLog[]>([])
const dialogVisible = ref(false)
const detailsDrawerVisible = ref(false)
const extendDialogVisible = ref(false)
const editingSubscription = ref<Subscription | null>(null)
const formRef = ref()
const extendingSubscription = ref<Subscription | null>(null)

const filterForm = ref({
  keyword: '',
  status: '',
})

const extendForm = ref({
  days: 30,
})

const formData = ref<FormData>({
  user_id: 0,
  plan_id: undefined,
  start_date: '',
  end_date: '',
  amount_paid: 0,
  payment_method: undefined,
  status: 'active',
})

const formRules = {
  user_id: [{ required: true, message: '请输入用户ID', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择过期时间', trigger: 'change' }],
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    expired: 'danger',
    cancelled: 'info',
    pending: 'warning',
  }
  return types[status] || 'info'
}

const loadSubscriptions = async () => {
  try {
    // TODO: 调用 API: GET /api/v1/subscriptions/admin
    // const response = await fetch('/api/v1/subscriptions/admin')
    // subscriptions.value = await response.json()
    // 模拟数据
    subscriptions.value = [
      {
        id: 1,
        user_id: 1,
        plan_id: 1,
        start_date: '2024-01-01T00:00:00Z',
        end_date: '2025-01-01T00:00:00Z',
        amount_paid: 99,
        payment_method: 'wechat',
        transaction_id: 'TXN001',
        status: 'active',
        notes: '测试订阅',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        is_valid: true,
        days_remaining: 100,
        plan: { id: 1, display_name: '月度套餐' },
      },
    ]
  } catch (error) {
    ElMessage.error('加载订阅列表失败')
  }
}

const loadPlans = async () => {
  try {
    // TODO: 调用 API: GET /api/v1/plans
    // const response = await fetch('/api/v1/plans')
    // plansOptions.value = await response.json()
    plansOptions.value = [
      { id: 1, display_name: '月度套餐', price: 99, duration_days: 30 },
      { id: 2, display_name: '季度套餐', price: 249, duration_days: 90 },
      { id: 3, display_name: '年度套餐', price: 699, duration_days: 365 },
    ]
  } catch (error) {
    ElMessage.error('加载套餐列表失败')
  }
}

const handleSearch = () => {
  // TODO: 实现搜索逻辑
  loadSubscriptions()
}

const handleReset = () => {
  filterForm.value = { keyword: '', status: '' }
  loadSubscriptions()
}

const handleCreateSubscription = () => {
  editingSubscription.value = null
  formData.value = {
    user_id: 0,
    plan_id: undefined,
    start_date: '',
    end_date: '',
    amount_paid: 0,
    payment_method: undefined,
    status: 'active',
  }
  dialogVisible.value = true
}

const handleEditSubscription = (subscription: Subscription) => {
  editingSubscription.value = subscription
  formData.value = {
    user_id: subscription.user_id,
    plan_id: subscription.plan_id,
    start_date: subscription.start_date,
    end_date: subscription.end_date,
    amount_paid: subscription.amount_paid,
    payment_method: subscription.payment_method,
    status: subscription.status,
  }
  dialogVisible.value = true
}

const handleSaveSubscription = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    if (editingSubscription.value) {
      // TODO: 调用编辑 API
      ElMessage.success('订阅已更新')
    } else {
      // TODO: 调用创建 API
      ElMessage.success('订阅已创建')
    }
    dialogVisible.value = false
    await loadSubscriptions()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleViewDetails = async (subscription: Subscription) => {
  selectedSubscription.value = subscription
  try {
    // TODO: 调用获取日志 API
    subscriptionLogs.value = []
  } catch (error) {
    ElMessage.error('加载日志失败')
  }
  detailsDrawerVisible.value = true
}

const handleExtendSubscription = (subscription: Subscription) => {
  extendingSubscription.value = subscription
  extendForm.value.days = 30
  extendDialogVisible.value = true
}

const handleConfirmExtend = async () => {
  if (!extendingSubscription.value) return
  try {
    // TODO: 调用延期 API: POST /api/v1/subscriptions/admin/{id}/extend
    ElMessage.success(`已延期 ${extendForm.value.days} 天`)
    extendDialogVisible.value = false
    await loadSubscriptions()
  } catch (error) {
    ElMessage.error('延期失败')
  }
}

const handleCancelSubscription = async (subscriptionId: number) => {
  try {
    // TODO: 调用取消 API (设置状态为 cancelled)
    ElMessage.success('订阅已取消')
    await loadSubscriptions()
  } catch (error) {
    ElMessage.error('取消失败')
  }
}

onMounted(async () => {
  await loadPlans()
  await loadSubscriptions()
})
</script>

<style scoped>
.subscription-management {
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

.filter-card {
  margin-bottom: 20px;
}

.user-cell {
  display: flex;
  align-items: center;
}

.username {
  font-weight: 500;
  color: #333;
}

.details-content {
  padding: 20px;
}

.logs-section {
  margin-top: 30px;
}

.logs-section h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 16px;
}

.log-action {
  display: inline-block;
  background: #f0f9ff;
  color: #0066cc;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 10px;
}

.log-detail {
  color: #666;
  font-size: 14px;
}
</style>
