<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <header class="bg-green-600 text-white p-4">
      <h1 class="text-xl font-bold text-center">成長（せいちょう）グラフ</h1>
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
        まだ記録がありません
      </div>
      
      <!-- Charts -->
      <div v-else>
        <div class="mb-4">
          <!-- Filter by plant type -->
          <select v-model="selectedPlant" @change="updateCharts" class="w-full p-2 border border-gray-300 rounded-lg">
            <option value="">全ての植物</option>
            <option value="向日葵（ひまわり）">向日葵（ひまわり）</option>
            <option value="秋桜（コスモス）">秋桜（コスモス）</option>
            <option value="朝顔（あさがお）">朝顔（あさがお）</option>
          </select>
        </div>

        <!-- Height Chart -->
        <div class="bg-white rounded-lg shadow p-4 mb-4">
          <h3 class="text-lg font-semibold mb-4">高さの推移</h3>
          <div class="h-64">
            <canvas ref="heightChart"></canvas>
          </div>
        </div>

        <!-- Temperature Chart -->
        <div class="bg-white rounded-lg shadow p-4 mb-4">
          <h3 class="text-lg font-semibold mb-4">気温の推移</h3>
          <div class="h-64">
            <canvas ref="temperatureChart"></canvas>
          </div>
        </div>

        <!-- Combined Chart -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-lg font-semibold mb-4">高さと気温の関係</h3>
          <div class="h-64">
            <canvas ref="combinedChart"></canvas>
          </div>
        </div>
      </div>
    </main>

    <!-- Tab Navigation -->
    <nav class="tab-navigation">
      <div class="flex">
        <NuxtLink to="/" class="tab-item inactive">
          <div class="text-2xl mb-1">📝</div>
          <div class="text-xs">入力<br>（にゅうりょく）</div>
        </NuxtLink>
        <NuxtLink to="/records" class="tab-item inactive">
          <div class="text-2xl mb-1">📋</div>
          <div class="text-xs">一覧<br>（いちらん）</div>
        </NuxtLink>
        <NuxtLink to="/graphs" class="tab-item active">
          <div class="text-2xl mb-1">📊</div>
          <div class="text-xs">グラフ</div>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useApi } from '~/composables/useApi'
import { useNotification } from '~/composables/useNotification'
import { getPlantName } from '~/utils/formatters'

// Register Chart.js components
Chart.register(...registerables)

// Composables
const { apiCall } = useApi()
const { showError } = useNotification()

// Data and state
const records = ref([])
const loading = ref(true)
const error = ref(null)
const selectedPlant = ref('')

// Chart refs
const heightChart = ref(null)
const temperatureChart = ref(null)
const combinedChart = ref(null)

// Chart instances
let heightChartInstance = null
let temperatureChartInstance = null
let combinedChartInstance = null

// Fetch records from API
const fetchRecords = async () => {
  loading.value = true
  const { data, error: apiError } = await apiCall('/api/records')
  
  if (apiError) {
    error.value = `データの取得に失敗しました: ${apiError}`
    showError(error.value)
  } else {
    records.value = (data || []).sort((a, b) => new Date(a.date) - new Date(b.date))
    error.value = null
  }
  
  loading.value = false
}

// Process data for charts
const processChartData = () => {
  const filteredRecords = selectedPlant.value 
    ? records.value.filter(record => 
        record.plants.some(plant => plant.type === selectedPlant.value)
      )
    : records.value

  const labels = filteredRecords.map(record => {
    const date = new Date(record.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })

  const plantTypes = selectedPlant.value ? [selectedPlant.value] : ['向日葵（ひまわり）', '秋桜（コスモス）', '朝顔（あさがお）']
  const plantColors = {
    '向日葵（ひまわり）': '#FCD34D',
    '秋桜（コスモス）': '#F472B6', 
    '朝顔（あさがお）': '#A78BFA'
  }

  const heightDatasets = plantTypes.map(plantType => {
    const data = filteredRecords.map(record => {
      const plant = record.plants.find(p => p.type === plantType)
      return plant ? plant.height : null
    })
    
    return {
      label: getPlantName(plantType),
      data: data,
      borderColor: plantColors[plantType],
      backgroundColor: plantColors[plantType] + '20',
      tension: 0.1,
      spanGaps: true
    }
  })

  const temperatureData = filteredRecords.map(record => record.temperature)

  return {
    labels,
    heightDatasets,
    temperatureData
  }
}

// Create height chart
const createHeightChart = () => {
  if (!heightChart.value) return
  
  const { labels, heightDatasets } = processChartData()
  
  if (heightChartInstance) {
    heightChartInstance.destroy()
  }
  
  heightChartInstance = new Chart(heightChart.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: heightDatasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '高さ (cm)'
          }
        },
        x: {
          title: {
            display: true,
            text: '日付'
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  })
}

// Create temperature chart
const createTemperatureChart = () => {
  if (!temperatureChart.value) return
  
  const { labels, temperatureData } = processChartData()
  
  if (temperatureChartInstance) {
    temperatureChartInstance.destroy()
  }
  
  temperatureChartInstance = new Chart(temperatureChart.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: '気温',
        data: temperatureData,
        borderColor: '#EF4444',
        backgroundColor: '#EF444420',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          title: {
            display: true,
            text: '気温 (°C)'
          }
        },
        x: {
          title: {
            display: true,
            text: '日付'
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  })
}

// Create combined chart
const createCombinedChart = () => {
  if (!combinedChart.value) return
  
  const { labels, heightDatasets, temperatureData } = processChartData()
  
  if (combinedChartInstance) {
    combinedChartInstance.destroy()
  }
  
  const datasets = [
    ...heightDatasets,
    {
      label: '気温',
      data: temperatureData,
      borderColor: '#EF4444',
      backgroundColor: '#EF444420',
      tension: 0.1,
      yAxisID: 'y1'
    }
  ]
  
  combinedChartInstance = new Chart(combinedChart.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: '高さ (cm)'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: '気温 (°C)'
          },
          grid: {
            drawOnChartArea: false,
          },
        },
        x: {
          title: {
            display: true,
            text: '日付'
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  })
}

// Update all charts
const updateCharts = async () => {
  await nextTick()
  createHeightChart()
  createTemperatureChart()
  createCombinedChart()
}

// Helper functions are now imported from utils

// Initialize
onMounted(async () => {
  await fetchRecords()
  if (records.value.length > 0) {
    await nextTick()
    updateCharts()
  }
})

// Cleanup on unmount
onUnmounted(() => {
  if (heightChartInstance) heightChartInstance.destroy()
  if (temperatureChartInstance) temperatureChartInstance.destroy()
  if (combinedChartInstance) combinedChartInstance.destroy()
})
</script>