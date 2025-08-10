<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <header class="bg-green-600 text-white p-4">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold flex-1 text-center">植物成長記録（しょくぶつせいちょうきろく）</h1>
        <div class="flex space-x-2">
          <!-- デバッグ用リフレッシュボタン -->
          <button @click="forceRefresh" class="text-white text-sm bg-green-700 px-2 py-1 rounded">
            🔄
          </button>
        </div>
      </div>
    </header>

    <!-- Content Area -->
    <main class="p-4 max-w-md mx-auto">
      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-lg shadow-md p-6 text-center">
        <div class="text-gray-500">読み込み中（よみこみちゅう）...</div>
      </div>

      <!-- Already Recorded Today -->
      <div v-else-if="todayRecord && !editMode" class="bg-white rounded-lg shadow-md p-6">
        <div class="text-center mb-6">
          <div class="text-4xl mb-2">✅</div>
          <h2 class="text-lg font-semibold text-green-600">今日（きょう）の記録（きろく）は入力済（にゅうりょくず）みです</h2>
          <p class="text-sm text-gray-600 mt-2">記録（きろく）の内容（ないよう）を確認（かくにん）できます</p>
        </div>
        <!-- Today's Record Display -->
        <div class="space-y-4">
          <div class="text-center">
            <div class="text-sm text-gray-500 mb-2">{{ currentDate }}</div>
          </div>
          
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div>天気（てんき）: {{ getWeatherIcon(todayRecord.weather) }} {{ getWeatherLabel(todayRecord.weather) }}</div>
            <div>気温（きおん）: {{ todayRecord.temperature }}°C</div>
          </div>
          
          <div class="space-y-3">
            <h3 class="text-md font-semibold text-gray-800">植物別記録（しょくぶつべつきろく）</h3>
            <div v-for="plant in todayRecord.plants" :key="plant.type" 
                 class="border border-gray-200 rounded-lg p-3">
              <div class="flex items-start space-x-3">
                <div v-if="plant.image" class="flex-shrink-0">
                  <img :src="getImageUrl(plant.image)" :alt="plant.type"
                       class="w-16 h-16 rounded-lg object-cover border border-gray-200">
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-800 mb-1">{{ getPlantNameWithFurigana(plant.type) }}</div>
                  <div v-if="plant.height" class="text-sm text-gray-600 mb-1">
                    高さ（たかさ）: {{ plant.height }}cm
                  </div>
                  <div v-if="plant.comment" class="text-sm text-gray-600">
                    {{ plant.comment }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="text-center text-sm text-gray-500 mt-4">
            記録時刻（きろくじこく）: {{ formatDateTime(todayRecord.createdAt) }}
          </div>
          
          <!-- Action Buttons -->
          <div class="mt-6 space-y-3">
            <div class="text-center text-sm text-gray-600 mb-2">
              記録（きろく）を変更（へんこう）したい場合は下（した）のボタンを押（お）してください
            </div>
            <button
              @click="goToEditRecord"
              class="w-full py-3 px-4 rounded-md font-medium bg-blue-600 hover:bg-blue-700 text-white transition-colors flex items-center justify-center space-x-2 shadow-md"
            >
              <span>✏️</span>
              <span>編集（へんしゅう）する</span>
            </button>
            
            <!-- View Records Button -->
            <button
              @click="goToRecords"
              class="w-full py-2 px-4 rounded-md font-medium bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors flex items-center justify-center space-x-2"
            >
              <span>📋</span>
              <span>記録一覧（きろくいちらん）を見る</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Input Form -->
      <div v-else>
        <RecordForm
          :is-edit-mode="false"
          :display-date="currentDate"
          @submit="handleSubmit"
        />
      </div>
    </main>

    <!-- Tab Navigation -->
    <nav class="tab-navigation">
      <div class="flex">
        <NuxtLink to="/" class="tab-item active">
          <div class="text-2xl mb-1">📝</div>
          <div class="text-xs">入力<br>（にゅうりょく）</div>
        </NuxtLink>
        <NuxtLink to="/records" class="tab-item inactive">
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
import { useApi } from '~/composables/useApi'
import { useNotification } from '~/composables/useNotification'
import { 
  formatCurrentDate, 
  formatDateTime, 
  getWeatherIcon, 
  getWeatherLabel, 
  getPlantNameWithFurigana 
} from '~/utils/formatters'

// Composables
const { apiCall } = useApi()
const { showSuccess, showError } = useNotification()
const config = useRuntimeConfig()

// 画像URLを完全なURLに変換する関数
const getImageUrl = (imagePath) => {
  if (!imagePath) return null
  if (imagePath.startsWith('http')) return imagePath
  if (imagePath.startsWith('/')) return imagePath
  return `${config.public.apiBase}${imagePath}`
}

// Reactive data
const loading = ref(true)
const todayRecord = ref(null)
const editMode = ref(false)

// Check today's record on mount
const checkTodayRecord = async () => {
  console.log('今日の記録をチェック中...', new Date().toISOString())
  
  // 毎回todayRecordを完全にリセット
  todayRecord.value = null
  loading.value = true
  
  // APIを呼び出し（force_dateパラメータなし）
  const { data, error } = await apiCall('/records/today')
  
  if (error) {
    console.error('今日の記録確認エラー:', error)
    showError(`今日の記録確認に失敗しました: ${error}`)
    todayRecord.value = null
  } else if (data?.exists) {
    console.log('今日の記録が見つかりました:', data.record)
    todayRecord.value = data.record
  } else {
    console.log('今日の記録は存在しません。新規入力フォームを表示します。')
    todayRecord.value = null
  }
  
  loading.value = false
}

// Mount hook
onMounted(() => {
  checkTodayRecord()
  
  // 日付変更を監視（1分ごとにチェック）
  const checkDateChange = () => {
    const currentDate = new Date().toDateString()
    
    // 前回チェック時の日付と比較
    if (window.lastCheckedDate && window.lastCheckedDate !== currentDate) {
      console.log('日付が変わりました。記録をリフレッシュします。')
      console.log(`前回: ${window.lastCheckedDate}, 現在: ${currentDate}`)
      // 状態を完全にリセット
      todayRecord.value = null
      checkTodayRecord()
    }
    
    window.lastCheckedDate = currentDate
  }
  
  // 初回設定
  window.lastCheckedDate = new Date().toDateString()
  
  // 1分ごとに日付変更をチェック
  const dateCheckInterval = setInterval(checkDateChange, 60000)
  
  // ページフォーカス時の再チェック
  const handleVisibilityChange = () => {
    if (!document.hidden) {
      // ページが表示された時に状態をリセットして再チェック
      console.log('ページがフォーカスされました。記録を再チェックします。')
      todayRecord.value = null
      checkTodayRecord()
    }
  }
  
  document.addEventListener('visibilitychange', handleVisibilityChange)
  
  // コンポーネントがアンマウントされる時にクリーンアップ
  onUnmounted(() => {
    clearInterval(dateCheckInterval)
    document.removeEventListener('visibilitychange', handleVisibilityChange)
  })
})

// Current date
const currentDate = computed(() => formatCurrentDate())

// Handle form submit
const handleSubmit = async ({ data, isEditMode, recordId }) => {
  try {
    // Call API for new record creation
  const { data: responseData, error } = await apiCall('/records', {
      method: 'POST',
      body: data
    })
    
    if (error) {
      showError(`保存に失敗しました: ${error}`)
    } else {
      showSuccess('記録を保存しました！')
      
      // Refresh today's record
      setTimeout(() => {
        checkTodayRecord()
      }, 1000)
    }
    
  } catch (error) {
    showError('予期しないエラーが発生しました')
  }
}

// Navigate to edit page directly
const goToEditRecord = () => {
  if (todayRecord.value) {
    // Navigate directly to edit page
    navigateTo(`/records/edit/${todayRecord.value.id}`)
  }
}

// Navigate to records list
const goToRecords = () => {
  navigateTo('/records')
}

// 強制リフレッシュ（デバッグ用）
const forceRefresh = async () => {
  console.log('=== 強制リフレッシュ開始 ===')
  
  // 詳細な日付情報を出力
  const now = new Date()
  console.log('システム時刻:', now.toISOString())
  console.log('ローカル時刻:', now.toString())
  
  todayRecord.value = null
  loading.value = true
  
  // APIを呼び出し
  console.log('APIを呼び出します')
  const { data, error } = await apiCall('/records/today')
  
  if (error) {
    console.error('強制リフレッシュエラー:', error)
    showError(`記録確認に失敗しました: ${error}`)
    todayRecord.value = null
  } else if (data?.exists) {
    console.log('今日の記録が見つかりました:', data.record)
    todayRecord.value = data.record
  } else {
    console.log('今日の記録は存在しません - 新規入力フォーム表示')
    todayRecord.value = null
  }
  
  loading.value = false
  console.log('=== 強制リフレッシュ完了 ===')
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