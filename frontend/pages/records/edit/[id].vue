<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <header class="bg-green-600 text-white p-4">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold">記録編集（きろくへんしゅう）</h1>
        <button 
          @click="goBack"
          class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
        >
          一覧に戻る
        </button>
      </div>
    </header>

    <!-- Content Area -->
    <main class="p-4 max-w-md mx-auto">
      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-lg shadow-md p-6 text-center">
        <div class="text-gray-500">読み込み中（よみこみちゅう）...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-white rounded-lg shadow-md p-6 text-center">
        <div class="text-red-500 mb-4">{{ error }}</div>
        <button 
          @click="fetchRecord"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          再試行
        </button>
      </div>

      <!-- Record Not Found -->
      <div v-else-if="!record" class="bg-white rounded-lg shadow-md p-6 text-center">
        <div class="text-gray-500 mb-4">記録が見つかりません</div>
        <button 
          @click="goBack"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          一覧に戻る
        </button>
      </div>

      <!-- Edit Form -->
      <div v-else>
        <RecordForm
          :is-edit-mode="true"
          :record-data="record"
          :record-id="recordId"
          :display-date="formatDate(record.date)"
          @submit="handleSubmit"
          @cancel="handleCancel"
        />
      </div>
    </main>

    <!-- Tab Navigation -->
    <nav class="tab-navigation">
      <div class="flex">
        <NuxtLink to="/" class="tab-item inactive">
          <div class="text-2xl mb-1">📝</div>
          <div class="text-xs">入力<br>（にゅうりょく）</div>
        </NuxtLink>
        <NuxtLink to="/records" class="tab-item active">
          <div class="text-2xl mb-1">📋</div>
          <div class="text-xs">一覧<br>（いちらん）</div>
        </NuxtLink>
        <NuxtLink to="/graphs" class="tab-item inactive">
          <div class="text-2xl mb-1">📊</div>
          <div class="text-xs">グラフ</div>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'
import { useNotification } from '~/composables/useNotification'
import { formatDate } from '~/utils/formatters'

// Composables
const { apiCall } = useApi()
const { showSuccess, showError } = useNotification()

// Route
const route = useRoute()
const router = useRouter()

// Reactive data
const record = ref(null)
const loading = ref(true)
const error = ref(null)

// Computed
const recordId = computed(() => route.params.id)

// Fetch record data
const fetchRecord = async () => {
  try {
    loading.value = true
    error.value = null
    
    const { data, error: apiError } = await apiCall(`/api/records/${recordId.value}`)
    
    if (apiError) {
      throw new Error(apiError)
    }
    
    record.value = data
  } catch (err) {
    error.value = `記録の取得に失敗しました: ${err.message}`
    showError(error.value)
  } finally {
    loading.value = false
  }
}

// Handle form submit
const handleSubmit = async ({ data, isEditMode, recordId }) => {
  try {
    const { data: responseData, error: apiError } = await apiCall(`/api/records/${recordId}`, {
      method: 'PUT',
      body: data
    })
    
    if (apiError) {
      throw new Error(apiError)
    }
    
    showSuccess('記録を更新しました！')
    
    // Navigate back to records list
    setTimeout(() => {
      router.push('/records')
    }, 1000)
    
  } catch (err) {
    showError(`更新に失敗しました: ${err.message}`)
  }
}

// Handle cancel
const handleCancel = () => {
  router.push('/records')
}

// Navigation
const goBack = () => {
  router.push('/records')
}

// Initialize on mount
onMounted(() => {
  fetchRecord()
})
</script>

<style scoped>
.tab-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 0.5rem 0;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0;
  text-decoration: none;
  transition: color 0.2s;
}

.tab-item.active {
  color: #059669;
}

.tab-item.inactive {
  color: #6b7280;
}

.tab-item.inactive:hover {
  color: #059669;
}
</style> 