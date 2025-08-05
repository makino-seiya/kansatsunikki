<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <header class="bg-green-600 text-white p-4">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold">記録一覧</h1>
        
      </div>
    </header>

    <!-- Content Area -->
    <main class="p-4">
      <!-- Loading -->
      <div v-if="loading" class="text-center text-gray-500 py-8">
        <div class="text-2xl mb-2">⏳</div>
        <div>データを読み込み中...</div>
      </div>
      
      <!-- Error -->
      <div v-else-if="error" class="text-center text-red-500 py-8">
        <div class="text-2xl mb-2">❌</div>
        <div>{{ error }}</div>
        <button @click="fetchRecords" class="mt-2 text-blue-600 underline">
          再試行
        </button>
      </div>
      
      <!-- No data -->
      <div v-else-if="records.length === 0" class="text-center text-gray-500 py-8">
        <div class="text-2xl mb-2">📝</div>
        <div>まだ記録がありません</div>
        <NuxtLink to="/" class="mt-4 inline-block bg-green-600 text-white px-4 py-2 rounded-lg">
          最初の記録を作成
        </NuxtLink>
      </div>
      
      <!-- Records List -->
      <div v-else class="space-y-4">
        <div v-for="record in records" :key="record.id" 
             class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <!-- Record Header -->
          <div class="flex justify-between items-start mb-3">
            <div class="flex-1">
              <div class="text-lg font-semibold text-gray-800 mb-1">
                {{ formatDate(record.date) }}
              </div>
              <div class="text-xs text-gray-500">
                登録日時: {{ formatDateTime(record.createdAt) }}
              </div>
            </div>
            <div class="flex space-x-2">
              <!-- Edit Button -->
              <NuxtLink 
                :to="`/records/edit/${record.id}`"
                class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
              >
                編集
              </NuxtLink>
            </div>
          </div>
          
          <!-- Weather Info -->
          <div class="grid grid-cols-2 gap-3 mb-4 p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center space-x-2">
              <span class="text-lg">{{ getWeatherIcon(record.weather) }}</span>
              <span class="text-sm text-gray-700">{{ getWeatherName(record.weather) }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-lg">🌡️</span>
              <span class="text-sm text-gray-700">{{ record.temperature }}°C</span>
            </div>
          </div>
          
          <!-- Plants -->
          <div class="space-y-3">
            <div v-for="plant in record.plants" :key="plant.type" 
                 class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="flex items-start space-x-3">
                <!-- Plant Image -->
                <div class="flex-shrink-0">
                  <img v-if="plant.image" 
                       :src="getImageUrl(plant.image)" 
                       :alt="getPlantName(plant.type)"
                       class="w-16 h-16 rounded-lg object-cover border border-gray-200"
                       @error="handleImageError">
                  <div v-else 
                       class="w-16 h-16 rounded-lg bg-gray-200 flex items-center justify-center">
                    <span class="text-2xl">{{ getPlantIcon(plant.type) }}</span>
                  </div>
                </div>
                
                <!-- Plant Info -->
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-800 mb-1">
                    {{ getPlantName(plant.type) }}
                  </div>
                  <div class="text-sm text-gray-600 mb-1">
                    高さ: {{ plant.height }}cm
                  </div>
                  <div v-if="plant.comment" class="text-sm text-gray-600 break-words">
                    {{ plant.comment }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Tab Navigation -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
      <div class="flex">
        <NuxtLink to="/" class="flex-1 flex flex-col items-center py-2 text-gray-500 hover:text-green-600 transition-colors">
          <div class="text-2xl mb-1">📝</div>
          <div class="text-xs">入力</div>
        </NuxtLink>
        <NuxtLink to="/records" class="flex-1 flex flex-col items-center py-2 text-green-600">
          <div class="text-2xl mb-1">📋</div>
          <div class="text-xs">一覧</div>
        </NuxtLink>
        <NuxtLink to="/graphs" class="flex-1 flex flex-col items-center py-2 text-gray-500 hover:text-green-600 transition-colors">
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
import { 
  formatDate, 
  formatDateTime, 
  getWeatherIcon, 
  getWeatherName, 
  getPlantName, 
  getPlantIcon
} from '~/utils/formatters'

// Composables
const { apiCall } = useApi()
const { showError } = useNotification()

// Data from API
const records = ref([])
const loading = ref(true)
const error = ref(null)

// Fetch records from API
const fetchRecords = async () => {
  try {
    loading.value = true
    error.value = null
    
    const { data, error: apiError } = await apiCall('/api/records')
    
    if (apiError) {
      throw new Error(apiError)
    }
    
    records.value = data || []
  } catch (err) {
    error.value = `データの取得に失敗しました: ${err.message}`
    showError(error.value)
  } finally {
    loading.value = false
  }
}

// Initialize data on component mount
onMounted(async () => {
  await fetchRecords()
})

// Helper functions
const config = useRuntimeConfig()

// 画像URLを完全なURLに変換
const getImageUrl = (imagePath) => {
  if (!imagePath) return null
  if (imagePath.startsWith('http')) return imagePath
  return `${config.public.apiBase}${imagePath}`
}
const handleImageError = (event) => {
  // 画像読み込みエラー時のフォールバック
  event.target.style.display = 'none'
  const fallback = event.target.nextElementSibling
  if (fallback) {
    fallback.style.display = 'flex'
  }
}
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