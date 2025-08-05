<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <header class="bg-green-600 text-white p-4">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold flex-1 text-center">植物成長記録（しょくぶつせいちょうきろく）</h1>
        <div class="flex space-x-2">
          <!-- テストページリンク -->
          <NuxtLink to="/test/1" class="text-white text-sm bg-blue-600 px-2 py-1 rounded hover:bg-blue-700">
            テスト
          </NuxtLink>
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
        <h2 class="text-lg font-semibold mb-4 text-center text-green-600">今日（きょう）の記録（きろく）は入力済（にゅうりょくず）みです</h2>
        
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
                  <img :src="plant.image" :alt="plant.type"
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
          
          <!-- Edit Button -->
          <div class="mt-6">
            <button
              @click="goToEditRecord"
              class="w-full py-3 px-4 rounded-md font-medium bg-blue-600 hover:bg-blue-700 text-white transition-colors"
            >
              編集（へんしゅう）する
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

// Reactive data
const loading = ref(true)
const todayRecord = ref(null)
const editMode = ref(false)

// Check today's record on mount
const checkTodayRecord = async () => {
  const jstDate = getJSTDate() // JST日付を取得
  console.log('今日の記録をチェック中（JST）...', jstDate, new Date().toISOString())
  
  // 毎回todayRecordを完全にリセット
  todayRecord.value = null
  loading.value = true
  
  // JST日付を指定してAPIを呼び出し
  const { data, error } = await apiCall(`/api/records/today?force_date=${jstDate}`)
  
  if (error) {
    console.error('今日の記録確認エラー:', error)
    showError(`今日の記録確認に失敗しました: ${error}`)
    todayRecord.value = null
  } else if (data?.exists) {
    const recordDate = data.record.date
    console.log('APIから取得した記録:', data.record)
    console.log('記録の日付:', recordDate, 'JST日付:', jstDate)
    
    // 記録の日付がJST日付と一致するかを厳密にチェック
    if (recordDate === jstDate) {
      console.log('今日の記録が見つかりました:', data.record)
      todayRecord.value = data.record
    } else {
      console.log('記録の日付が今日と一致しません。新規入力フォームを表示します。')
      console.log(`記録日付: ${recordDate}, JST日付: ${jstDate}`)
      todayRecord.value = null
    }
  } else {
    console.log('今日の記録は存在しません。新規入力フォームを表示します。')
    todayRecord.value = null
  }
  
  loading.value = false
}

// Mount hook
onMounted(() => {
  checkTodayRecord()
  
  // 日付変更を監視（1分ごとにチェック）- JST対応
  const checkDateChange = () => {
    const currentJSTDate = getJSTDate()
    
    // 前回チェック時の日付と比較
    if (window.lastCheckedJSTDate && window.lastCheckedJSTDate !== currentJSTDate) {
      console.log('JST日付が変わりました。記録をリフレッシュします。')
      console.log(`前回: ${window.lastCheckedJSTDate}, 現在: ${currentJSTDate}`)
      // 状態を完全にリセット
      todayRecord.value = null
      checkTodayRecord()
    }
    
    window.lastCheckedJSTDate = currentJSTDate
  }
  
  // 初回設定
  window.lastCheckedJSTDate = getJSTDate()
  
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
    const { data: responseData, error } = await apiCall('/api/records', {
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

// JST（日本標準時）で今日の日付を取得する関数
const getJSTDate = () => {
  const now = new Date()
  // JST = UTC + 9時間
  const jstOffset = 9 * 60 // 9時間を分に変換
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000) // UTC時刻を取得
  const jst = new Date(utc + (jstOffset * 60000)) // JST時刻を計算
  
  const year = jst.getFullYear()
  const month = String(jst.getMonth() + 1).padStart(2, '0')
  const day = String(jst.getDate()).padStart(2, '0')
  
  return `${year}-${month}-${day}`
}

// 強制リフレッシュ（デバッグ用）
const forceRefresh = async () => {
  console.log('=== 強制リフレッシュ開始（JST対応版） ===')
  
  // 詳細な日付情報を出力
  const now = new Date()
  console.log('システム時刻 (UTC):', now.toISOString())
  console.log('システム時刻 (ローカル):', now.toString())
  console.log('タイムゾーンオフセット:', now.getTimezoneOffset(), '分')
  
  // JST時刻を計算
  const jstDate = getJSTDate()
  console.log('計算されたJST日付:', jstDate)
  
  // 比較用にUTC日付も表示
  const utcDate = now.toISOString().split('T')[0]
  console.log('UTC日付:', utcDate)
  
  todayRecord.value = null
  loading.value = true
  
  // JST日付でAPIを呼び出し
  console.log('JST日付でAPIを呼び出します:', jstDate)
  const { data, error } = await apiCall(`/api/records/today?force_date=${jstDate}`)
  
  if (error) {
    console.error('強制リフレッシュエラー:', error)
    showError(`記録確認に失敗しました: ${error}`)
    todayRecord.value = null
  } else if (data?.exists) {
    const recordDate = data.record.date
    console.log('APIから取得した記録:', data.record)
    console.log('記録の日付:', recordDate, 'JST日付:', jstDate)
    
    if (recordDate === jstDate) {
      console.log('日付が一致しました。既存記録を表示します。')
      todayRecord.value = data.record
    } else {
      console.log('日付が一致しません。新規入力フォームを表示します。')
      todayRecord.value = null
    }
  } else {
    console.log('JST日付での記録は存在しません - 新規入力フォーム表示')
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