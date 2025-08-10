<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-lg font-semibold mb-4 text-center">
      {{ isEditMode ? '記録（きろく）を編集（へんしゅう）' : '今日（きょう）の記録（きろく）' }}
    </h2>
    
    <!-- Date Display -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">日付（ひづけ）</label>
      <div class="bg-gray-100 p-3 rounded-md text-center">
        {{ displayDate }}
      </div>
    </div>

    <!-- Weather Selection -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">天気（てんき）</label>
      <div class="grid grid-cols-4 gap-2">
        <button
          v-for="weather in weatherOptions"
          :key="weather.value"
          @click="form.weather = weather.value"
          :class="[
            'p-3 rounded-md border-2 text-center transition-colors',
            form.weather === weather.value
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          ]"
        >
          <div class="text-2xl mb-1">{{ weather.icon }}</div>
          <div class="text-xs">{{ weather.label }}</div>
        </button>
      </div>
    </div>

    <!-- Temperature Input -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">気温（きおん） (°C)</label>
      <div class="space-y-3">
        <!-- 現在の温度表示 -->
        <div class="text-center">
          <span class="text-2xl font-bold text-blue-600">{{ form.temperature || 20 }}°C</span>
        </div>
        <!-- スライダー -->
        <div class="relative">
          <input
            v-model.number="form.temperature"
            type="range"
            min="-10"
            max="40"
            step="0.5"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            :style="{ background: getSliderBackground(form.temperature || 20) }"
          />
          <!-- 目盛り表示 -->
          <div class="flex justify-between text-xs text-gray-500 mt-1">
            <span>-10°C</span>
            <span>0°C</span>
            <span>20°C</span>
            <span>40°C</span>
          </div>
        </div>
        <!-- 微調整用の数値入力（オプション） -->
        <div class="flex items-center justify-center space-x-2">
          <button 
            @click="adjustTemperature(-0.5)"
            class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center hover:bg-gray-300"
            type="button"
          >
            -
          </button>
          <input
            v-model.number="form.temperature"
            type="number"
            step="0.5"
            min="-10"
            max="40"
            class="w-20 text-center p-1 border border-gray-300 rounded text-sm"
          />
          <button 
            @click="adjustTemperature(0.5)"
            class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center hover:bg-gray-300"
            type="button"
          >
            +
          </button>
        </div>
      </div>
    </div>

    <!-- Plant Records Section -->
    <div class="space-y-6">
      <h3 class="text-md font-semibold text-gray-800">植物別記録（しょくぶつべつきろく）</h3>
      
      <div
        v-for="plant in plants"
        :key="plant.id"
        class="border border-gray-200 rounded-lg p-4"
      >
        <h4 class="font-medium text-gray-800 mb-3 flex items-center">
          <span class="text-lg mr-2">{{ plant.icon }}</span>
          {{ plant.name }}
        </h4>
        
        <!-- Height Input -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-gray-700 mb-1">高さ（たかさ） (cm：センチメートル)</label>
          <input
            v-model="form.plantRecords[plant.id].height"
            type="number"
            step="0.1"
            class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="例（れい）: 15.5"
          />
        </div>

        <!-- Photo Upload -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-gray-700 mb-1">写真（しゃしん）</label>
          
          <!-- 既存画像の表示（編集モード時） -->
          <div v-if="isEditMode && form.plantRecords[plant.id].existingImage && !form.plantRecords[plant.id].imagePreview" class="mb-2">
            <div class="relative">
              <img
                :src="getImageUrl(form.plantRecords[plant.id].existingImage)"
                alt="既存の画像"
                class="w-full h-32 object-cover rounded-md border border-gray-200"
              />
              <button
                @click="removeExistingImage(plant.id)"
                class="absolute top-1 right-1 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                title="画像を削除"
              >
                ×
              </button>
            </div>
            <div class="mt-1 text-xs text-gray-500">現在の画像</div>
          </div>
          
          <input
            type="file"
            accept="image/*"
            @change="handleImageUpload($event, plant.id)"
            class="w-full p-2 border border-gray-300 rounded-md"
          />
          
          <!-- 新規アップロード画像のプレビュー -->
          <div v-if="form.plantRecords[plant.id].imagePreview" class="mt-2">
            <img
              :src="form.plantRecords[plant.id].imagePreview"
              alt="プレビュー"
              class="w-full h-32 object-cover rounded-md border border-blue-200"
            />
            <div class="mt-1 text-xs text-blue-500">新しい画像（プレビュー）</div>
          </div>
        </div>

        <!-- Comment Input -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">コメント</label>
          <textarea
            v-model="form.plantRecords[plant.id].comment"
            rows="2"
            class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="今日（きょう）の様子（ようす）を記録（きろく）しましょう"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="mt-6 flex space-x-3">
      <button
        v-if="isEditMode"
        @click="$emit('cancel')"
        class="flex-1 py-3 px-4 rounded-md font-medium bg-gray-500 hover:bg-gray-600 text-white transition-colors"
      >
        キャンセル
      </button>
      
      <button
        @click="handleSubmit"
        :disabled="!canSave || saving"
        :class="[
          'flex-1 py-3 px-4 rounded-md font-medium transition-colors',
          canSave && !saving
            ? 'bg-green-600 hover:bg-green-700 text-white'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        ]"
      >
        {{ saving ? '保存中（ほぞんちゅう）...' : (isEditMode ? '更新（こうしん）' : '記録（きろく）を保存（ほぞん）') }}
      </button>
    </div>

    <!-- Form Errors -->
    <div v-if="Object.keys(formErrors).length > 0" class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
      <div class="font-medium mb-2">入力エラー:</div>
      <ul class="list-disc list-inside text-sm">
        <li v-if="formErrors.weather">{{ formErrors.weather }}</li>
        <li v-if="formErrors.temperature">{{ formErrors.temperature }}</li>
        <li v-for="(plantError, plantId) in formErrors.plants" :key="plantId">
          <span v-if="plantError.height">植物{{ plantId }}: {{ plantError.height }}</span>
          <span v-if="plantError.image">植物{{ plantId }}: {{ plantError.image }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useNotification } from '~/composables/useNotification'
import { validateRecordForm, validateImage } from '~/utils/validation'
import { formatCurrentDate } from '~/utils/formatters'

// Props
const props = defineProps({
  isEditMode: {
    type: Boolean,
    default: false
  },
  recordData: {
    type: Object,
    default: null
  },
  recordId: {
    type: [String, Number],
    default: null
  },
  displayDate: {
    type: String,
    default: () => formatCurrentDate()
  }
})

// Emits
const emit = defineEmits(['submit', 'cancel'])

// Composables
const { apiCall, uploadImage } = useApi()
const { showSuccess, showError, showWarning } = useNotification()
const config = useRuntimeConfig()

// 画像URLを完全なURLに変換
const getImageUrl = (imagePath) => {
  if (!imagePath) return null
  if (imagePath.startsWith('http')) return imagePath
  if (imagePath.startsWith('/')) return imagePath
  return `${config.public.apiBase}${imagePath}`
}

// Reactive data
const form = ref({
  weather: '',
  temperature: 20,
  plantRecords: {
    1: { height: '', comment: '', image: null, imagePreview: null, existingImage: null },
    2: { height: '', comment: '', image: null, imagePreview: null, existingImage: null },
    3: { height: '', comment: '', image: null, imagePreview: null, existingImage: null }
  }
})

const saving = ref(false)
const formErrors = ref({})

// Weather options
const weatherOptions = [
  { value: 'sunny', label: '晴れ（はれ）', icon: '☀️' },
  { value: 'cloudy', label: '曇り（くもり）', icon: '☁️' },
  { value: 'rainy', label: '雨（あめ）', icon: '🌧️' },
  { value: 'thunder', label: '雷（かみなり）', icon: '⛈️' }
]

// Plant data
const plants = [
  { id: 1, name: '向日葵（ひまわり）', icon: '🌻' },
  { id: 2, name: '秋桜（コスモス）', icon: '🌸' },
  { id: 3, name: '朝顔（あさがお）', icon: '🌺' }
]

// Initialize form with record data (for edit mode)
watch(() => props.recordData, (newData) => {
  if (newData && props.isEditMode) {
    form.value.weather = newData.weather || ''
    form.value.temperature = newData.temperature || 20
    
    // Initialize plant records
    plants.forEach(plant => {
      const plantData = newData.plants?.find(p => p.type === plant.id) || {}
      form.value.plantRecords[plant.id] = {
        height: plantData.height || '',
        comment: plantData.comment || '',
        image: null,
        imagePreview: null,
        existingImage: plantData.image || null
      }
    })
  }
}, { immediate: true })

// Validation
const canSave = computed(() => {
  const validation = validateRecordForm(form.value)
  return validation.isValid
})

// Image upload handler
const handleImageUpload = (event, plantId) => {
  const file = event.target.files[0]
  if (!file) return

  // バリデーション
  const validation = validateImage(file)
  if (validation) {
    showError(validation)
    return
  }

  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    form.value.plantRecords[plantId].imagePreview = e.target.result
    form.value.plantRecords[plantId].image = file
    // 新しい画像を選択したら既存画像は非表示にする
    form.value.plantRecords[plantId].existingImage = null
  }
  reader.readAsDataURL(file)
}

// Submit handler
const handleSubmit = async () => {
  // バリデーション
  const validation = validateRecordForm(form.value)
  if (!validation.isValid) {
    formErrors.value = validation.errors
    showError('入力内容に問題があります')
    return
  }

  saving.value = true
  formErrors.value = {}

  try {
    // Upload images first
    const plantRecordsWithImages = { ...form.value.plantRecords }
    
    for (const plantId in plantRecordsWithImages) {
      const plantRecord = plantRecordsWithImages[plantId]
      if (plantRecord.image) {
        // 新しい画像がアップロードされた場合
        const { data: uploadData, error: uploadError } = await uploadImage(plantRecord.image)
        
        if (uploadError) {
          showWarning(`画像のアップロードに失敗しました: ${uploadError}`)
        } else {
          plantRecord.imageFilename = uploadData.filename
        }
      } else if (plantRecord.existingImage) {
        // 新しい画像がなく、既存の画像がある場合
        // 既存の画像のファイル名を抽出
        const imagePath = plantRecord.existingImage
        const filename = imagePath.split('/').pop() // /api/images/filename.png から filename.png を取得
        plantRecord.imageFilename = filename
      } else {
        // 新しい画像も既存の画像もない場合
        plantRecord.imageFilename = null
      }
      
      // Remove image and imagePreview from the data sent to API
      delete plantRecord.image
      delete plantRecord.imagePreview
      delete plantRecord.existingImage
    }
    
    // Prepare data for API
    const recordData = {
      weather: form.value.weather,
      temperature: form.value.temperature,
      plantRecords: plantRecordsWithImages
    }
    
    // Emit submit event with data
    emit('submit', {
      data: recordData,
      isEditMode: props.isEditMode,
      recordId: props.recordId
    })
    
  } catch (error) {
    showError('予期しないエラーが発生しました')
  } finally {
    saving.value = false
  }
}

// Helper functions
const getSliderBackground = (temperature) => {
  const temp = temperature || 20
  const percentage = ((temp + 10) / 50) * 100
  return `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${percentage}%, #E5E7EB ${percentage}%, #E5E7EB 100%)`
}

const adjustTemperature = (delta) => {
  const current = form.value.temperature || 20
  const newTemp = Math.max(-10, Math.min(40, current + delta))
  form.value.temperature = Math.round(newTemp * 2) / 2
}

// 既存画像を削除する関数
const removeExistingImage = (plantId) => {
  form.value.plantRecords[plantId].existingImage = null
  form.value.plantRecords[plantId].imageFilename = null
}
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: none;
}
</style> 