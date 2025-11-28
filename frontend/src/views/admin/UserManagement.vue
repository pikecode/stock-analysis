<template>
  <div class="user-management">
    <div class="header">
      <h1>用户管理</h1>
      <el-button type="primary" @click="handleAddUser">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <!-- 搜索和过滤 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索用户名、邮箱或手机"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="8">
          <el-select
            v-model="filterForm.status"
            placeholder="用户状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="user-list-card">
      <el-table :data="users" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="150" />
        <el-table-column prop="phone" label="手机" width="130" />
        <el-table-column label="订阅状态" width="180">
          <template #default="{ row }">
            <div v-if="row.subscription" class="subscription-status">
              <el-tag :type="getSubscriptionType(row.subscription)">
                {{ row.subscription.status }}
              </el-tag>
              <span class="subscription-plan">{{ row.subscription.plan_name }}</span>
            </div>
            <span v-else class="no-subscription">未订阅</span>
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="180">
          <template #default="{ row }">
            <div v-if="row.subscription" :class="['subscription-date', { expired: row.subscription.is_expired }]">
              <span class="start-date">{{ formatDate(row.subscription.start_date) }}</span>
              <span class="separator">→</span>
              <span class="end-date">{{ formatDate(row.subscription.end_date) }}</span>
              <el-tag v-if="!row.subscription.is_expired" type="success" size="small" class="days-remaining">
                剩余 {{ row.subscription.days_remaining }} 天
              </el-tag>
              <el-tag v-else type="danger" size="small" class="days-remaining">
                已过期
              </el-tag>
            </div>
            <span v-else class="no-subscription">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewUser(row)">详情</el-button>
            <el-button link type="primary" size="small" @click="handleManageSubscription(row)">
              {{ row.subscription ? '修改' : '添加' }}订阅
            </el-button>
            <el-button
              v-if="row.subscription && !row.subscription.is_expired"
              link
              type="success"
              size="small"
              @click="handleExtend(row)">
              延期
            </el-button>
            <el-button link type="danger" size="small" @click="handleDeleteUser(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 用户详情抽屉 -->
    <el-drawer v-model="detailsVisible" title="用户详情" size="40%">
      <div v-if="selectedUser" class="user-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ selectedUser.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedUser.email }}</el-descriptions-item>
          <el-descriptions-item label="手机">{{ selectedUser.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="账户状态">
            <el-tag :type="selectedUser.status === 'active' ? 'success' : 'info'">
              {{ selectedUser.status === 'active' ? '活跃' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(selectedUser.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后登录">
            {{ selectedUser.last_login_at ? formatDate(selectedUser.last_login_at) : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedUser?.subscription" class="subscription-details">
          <h3>订阅信息</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="套餐">
              {{ selectedUser.subscription?.plan_name }}
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">
              {{ formatDate(selectedUser.subscription?.start_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="结束时间">
              {{ formatDate(selectedUser.subscription?.end_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="剩余天数">
              <el-tag :type="selectedUser.subscription?.is_expired ? 'danger' : 'success'">
                {{ selectedUser.subscription?.is_expired ? '已过期' : `${selectedUser.subscription?.days_remaining} 天` }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="支付金额">
              ¥{{ (Number(selectedUser.subscription?.amount_paid) || 0).toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="支付方式">
              {{ selectedUser.subscription?.payment_method || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-drawer>

    <!-- 订阅管理对话框 -->
    <el-dialog
      v-model="subscriptionDialogVisible"
      :title="`${selectedUser?.username} - ${editingSubscription ? '修改' : '添加'}订阅`"
      width="500px"
    >
      <el-form
        :model="subscriptionForm"
        :rules="subscriptionRules"
        label-width="100px"
        ref="subscriptionFormRef"
      >
        <el-form-item label="套餐" prop="plan_id">
          <el-select v-model="subscriptionForm.plan_id" placeholder="选择套餐">
            <el-option
              v-for="plan in plans"
              :key="plan.id"
              :label="`${plan.display_name} (¥${plan.price}/${plan.duration_days}天)`"
              :value="plan.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_date">
          <el-date-picker
            v-model="subscriptionForm.start_date"
            type="datetime"
            placeholder="选择开始时间"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_date">
          <el-date-picker
            v-model="subscriptionForm.end_date"
            type="datetime"
            placeholder="选择结束时间"
          />
        </el-form-item>
        <el-form-item label="支付金额" prop="amount_paid">
          <el-input-number
            v-model="subscriptionForm.amount_paid"
            :precision="2"
            :min="0"
            placeholder="0.00"
          />
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="subscriptionForm.payment_method" placeholder="选择支付方式" clearable>
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="手动" value="manual" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subscriptionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveSubscription">保存</el-button>
      </template>
    </el-dialog>

    <!-- 延期对话框 -->
    <el-dialog v-model="extendDialogVisible" title="延期订阅" width="400px">
      <el-form :model="extendForm" label-width="100px">
        <el-form-item label="延期天数">
          <el-input-number
            v-model="extendForm.days"
            :min="1"
            :max="365"
            placeholder="30"
          />
        </el-form-item>
        <el-form-item label="当前有效期">
          <span v-if="selectedUser?.subscription">
            {{ formatDate(selectedUser.subscription.start_date) }} →
            {{ formatDate(selectedUser.subscription.end_date) }}
          </span>
        </el-form-item>
        <el-form-item label="延期后有效期">
          <span v-if="selectedUser?.subscription && extendForm.days">
            {{ formatDate(selectedUser.subscription.start_date) }} →
            {{ formatDate(getExtendedDate(selectedUser.subscription.end_date, extendForm.days)) }}
          </span>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { usersApi, subscriptionApi, plansApi } from '@/api'

interface User {
  id: number
  username: string
  email: string
  phone?: string
  status: string
  created_at: string
  last_login_at?: string
  subscription?: UserSubscription
}

interface UserSubscription {
  id: number
  plan_name: string
  start_date: string
  end_date: string
  amount_paid: number
  payment_method?: string
  status: string
  is_expired: boolean
  days_remaining: number
}

interface Plan {
  id: number
  name: string
  display_name: string
  price: number
  duration_days: number
}

interface SubscriptionFormData {
  plan_id?: number
  start_date: Date
  end_date: Date
  amount_paid: number
  payment_method?: string
}

const users = ref<User[]>([])
const plans = ref<Plan[]>([])
const selectedUser = ref<User | null>(null)
const loading = ref(false)
const detailsVisible = ref(false)
const subscriptionDialogVisible = ref(false)
const extendDialogVisible = ref(false)
const editingSubscription = ref(false)
const subscriptionFormRef = ref()

const filterForm = ref({
  keyword: '',
  status: '',
})

const subscriptionForm = ref<SubscriptionFormData>({
  plan_id: undefined,
  start_date: new Date(),
  end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
  amount_paid: 0,
  payment_method: undefined,
})

const extendForm = ref({
  days: 30,
})

const subscriptionRules = {
  plan_id: [{ required: true, message: '请选择套餐', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
}

const formatDate = (date: string | Date | undefined) => {
  if (!date) return '-'
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getSubscriptionType = (subscription: UserSubscription) => {
  if (subscription.is_expired) return 'danger'
  if (subscription.days_remaining < 7) return 'warning'
  return 'success'
}

const getExtendedDate = (endDate: string, days: number) => {
  const date = new Date(endDate)
  date.setDate(date.getDate() + days)
  return formatDate(date.toISOString())
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      keyword: filterForm.value.keyword || undefined,
      status: filterForm.value.status || undefined,
    }
    const data = await usersApi.listUsers(params)
    users.value = data as User[]
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadPlans = async () => {
  try {
    const data = await plansApi.getList()
    plans.value = data as Plan[]
  } catch (error) {
    ElMessage.error('加载套餐列表失败')
    console.error(error)
  }
}

const handleSearch = () => {
  loadUsers()
}

const handleReset = () => {
  filterForm.value = { keyword: '', status: '' }
  loadUsers()
}

const handleAddUser = () => {
  ElMessage.info('用户新增功能开发中...')
}

const handleViewUser = async (user: User) => {
  try {
    const data = await usersApi.getUser(user.id)
    selectedUser.value = data as User
    detailsVisible.value = true
  } catch (error) {
    ElMessage.error('加载用户详情失败')
  }
}

const handleManageSubscription = (user: User) => {
  selectedUser.value = user
  editingSubscription.value = !!user.subscription

  if (user.subscription) {
    // 根据plan_name查找对应的plan_id
    const matchedPlan = plans.value.find(
      (plan) => plan.display_name === user.subscription?.plan_name
    )

    subscriptionForm.value = {
      plan_id: matchedPlan?.id,
      start_date: new Date(user.subscription.start_date),
      end_date: new Date(user.subscription.end_date),
      amount_paid: user.subscription.amount_paid,
      payment_method: user.subscription.payment_method,
    }
  } else {
    const now = new Date()
    subscriptionForm.value = {
      plan_id: undefined,
      start_date: now,
      end_date: new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000),
      amount_paid: 0,
      payment_method: undefined,
    }
  }

  subscriptionDialogVisible.value = true
}

const handleSaveSubscription = async () => {
  if (!subscriptionFormRef.value || !selectedUser.value) return
  await subscriptionFormRef.value.validate()

  try {
    const payload = {
      user_id: selectedUser.value.id,
      plan_id: subscriptionForm.value.plan_id,
      start_date: subscriptionForm.value.start_date,
      end_date: subscriptionForm.value.end_date,
      amount_paid: subscriptionForm.value.amount_paid,
      payment_method: subscriptionForm.value.payment_method,
      status: 'active',
    }

    if (editingSubscription.value && selectedUser.value.subscription) {
      // 调用编辑 API: PUT /api/v1/subscriptions/admin/{id}
      await subscriptionApi.update(selectedUser.value.subscription.id, payload)
      ElMessage.success('订阅已更新')
    } else {
      // 调用创建 API: POST /api/v1/subscriptions/admin
      await subscriptionApi.create(payload)
      ElMessage.success('订阅已创建')
    }
    subscriptionDialogVisible.value = false
    await loadUsers()
  } catch (error) {
    ElMessage.error('保存订阅失败')
    console.error(error)
  }
}

const handleExtend = (user: User) => {
  selectedUser.value = user
  extendForm.value.days = 30
  extendDialogVisible.value = true
}

const handleConfirmExtend = async () => {
  if (!selectedUser.value?.subscription) return

  try {
    // 调用延期 API: POST /api/v1/subscriptions/admin/{id}/extend
    await subscriptionApi.extend(selectedUser.value.subscription.id, extendForm.value.days)
    ElMessage.success(`已延期 ${extendForm.value.days} 天`)
    extendDialogVisible.value = false
    await loadUsers()
  } catch (error) {
    ElMessage.error('延期失败')
    console.error(error)
  }
}

const handleDeleteUser = async (userId: number) => {
  ElMessageBox.confirm('确定要删除该用户吗？此操作不可撤销。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        // 调用删除 API: DELETE /api/v1/users/admin/{userId}
        await usersApi.deleteUser(userId)
        ElMessage.success('用户已删除')
        await loadUsers()
      } catch (error) {
        ElMessage.error('删除失败')
        console.error(error)
      }
    })
    .catch(() => {
      ElMessage.info('删除已取消')
    })
}

onMounted(async () => {
  await loadPlans()
  await loadUsers()
})
</script>

<style scoped>
.user-management {
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

.user-list-card {
  margin-bottom: 20px;
}

.subscription-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.subscription-plan {
  font-size: 12px;
  color: #909399;
}

.no-subscription {
  color: #909399;
  font-style: italic;
}

.subscription-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.subscription-date.expired {
  color: #f56c6c;
}

.subscription-date .separator {
  color: #909399;
}

.days-remaining {
  margin-left: 8px;
}

.user-details {
  padding: 20px;
}

.subscription-details {
  margin-top: 30px;
}

.subscription-details h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

:deep(.el-dialog__title) {
  font-size: 16px;
}
</style>
