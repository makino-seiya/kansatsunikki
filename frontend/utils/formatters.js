// 日付・時刻フォーマット関数
export const formatDate = (dateString) => {
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}年${month}月${day}日`
}

export const formatDateTime = (dateTimeString) => {
  const date = new Date(dateTimeString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')

  return `${year}年${month}月${day}日 ${hour}:${minute}`
}

export const formatCurrentDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  const weekdays = [
    '日（にち）曜日（ようび）',
    '月（げつ）曜日（ようび）',
    '火（か）曜日（ようび）',
    '水（すい）曜日（ようび）',
    '木（もく）曜日（ようび）',
    '金（きん）曜日（ようび）',
    '土（ど）曜日（ようび）'
  ]
  const weekday = weekdays[today.getDay()]

  return `${year}年${month}月${day}日 ${weekday}`
}

// 天気関連の変換関数
export const getWeatherIcon = (weather) => {
  const icons = {
    'sunny': '☀️',
    'cloudy': '☁️',
    'rainy': '🌧️',
    'thunder': '⛈️',
    '晴れ': '☀️',
    '曇り': '☁️',
    '雨': '🌧️',
    '雷': '⛈️'
  }
  return icons[weather] || '☀️'
}

export const getWeatherName = (weather) => {
  const names = {
    'sunny': '晴れ',
    'cloudy': '曇り',
    'rainy': '雨',
    'thunder': '雷',
    '晴れ': '晴れ',
    '曇り': '曇り',
    '雨': '雨',
    '雷': '雷'
  }
  return names[weather] || weather
}

export const getWeatherLabel = (weather) => {
  const labels = {
    'sunny': '晴れ（はれ）',
    'cloudy': '曇り（くもり）',
    'rainy': '雨（あめ）',
    'thunder': '雷（かみなり）'
  }
  return labels[weather] || weather
}

// 植物関連の変換関数
export const getPlantName = (type) => {
  const names = {
    '向日葵（ひまわり）': '向日葵（ひまわり）',
    '秋桜（コスモス）': '秋桜（コスモス）',
    '朝顔': '朝顔（あさがお）',
    '朝顔（あさがお）': '朝顔（あさがお）',
    'ひまわり': '向日葵（ひまわり）',
    'コスモス': '秋桜（コスモス）',
    'sunflower': 'ひまわり',
    'cosmos': 'コスモス',
    'morning-glory': '朝顔（あさがお）'
  }
  return names[type] || type
}

export const getPlantIcon = (type) => {
  const icons = {
    '向日葵（ひまわり）': '🌻',
    '秋桜（コスモス）': '🌸',
    '朝顔（あさがお）': '🌺',
    'sunflower': '🌻',
    'cosmos': '🌸',
    'morning-glory': '🌺'
  }
  return icons[type] || '🌱'
}

export const getPlantNameWithFurigana = (plantName) => {
  const names = {
    '向日葵（ひまわり）': '向日葵（ひまわり）',
    '秋桜（コスモス）': '秋桜（コスモス）',
    '朝顔': '朝顔（あさがお）',
    '朝顔（あさがお）': '朝顔（あさがお）'
  }
  return names[plantName] || plantName
}

// 天気の英語→日本語変換
export const convertWeatherToJapanese = (weather) => {
  const weatherMapping = {
    'sunny': '晴れ',
    'cloudy': '曇り',
    'rainy': '雨',
    'thunder': '雷'
  }
  return weatherMapping[weather] || weather
}