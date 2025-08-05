// バリデーション関数
export const validateRequired = (value, fieldName = 'この項目') => {
  if (!value || value.toString().trim() === '') {
    return `${fieldName}は必須です`
  }
  return null
}

export const validateNumber = (value, fieldName = 'この項目', min = null, max = null) => {
  if (value === null || value === undefined || value === '') {
    return null // 空の場合はスキップ（必須チェックは別で行う）
  }
  
  const num = parseFloat(value)
  if (isNaN(num)) {
    return `${fieldName}は数値で入力してください`
  }
  
  if (min !== null && num < min) {
    return `${fieldName}は${min}以上で入力してください`
  }
  
  if (max !== null && num > max) {
    return `${fieldName}は${max}以下で入力してください`
  }
  
  return null
}

export const validateTemperature = (value) => {
  return validateNumber(value, '気温', -50, 60)
}

export const validateHeight = (value) => {
  return validateNumber(value, '高さ', 0, 1000)
}

export const validateImage = (file) => {
  if (!file) return null
  
  // ファイルタイプチェック
  if (!file.type.startsWith('image/')) {
    return '画像ファイルのみアップロード可能です'
  }
  
  // ファイルサイズチェック（3MB）
  const maxSize = 3 * 1024 * 1024
  if (file.size > maxSize) {
    return 'ファイルサイズは3MB以下にしてください'
  }
  
  return null
}

export const validateWeather = (weather) => {
  const validWeathers = ['sunny', 'cloudy', 'rainy', 'thunder', '晴れ', '曇り', '雨', '雷']
  if (!validWeathers.includes(weather)) {
    return '有効な天気を選択してください'
  }
  return null
}

// フォーム全体のバリデーション
export const validateRecordForm = (form) => {
  const errors = {}
  
  // 天気のバリデーション
  const weatherError = validateRequired(form.weather, '天気')
  if (weatherError) errors.weather = weatherError
  
  // 気温のバリデーション
  const tempRequiredError = validateRequired(form.temperature, '気温')
  if (tempRequiredError) {
    errors.temperature = tempRequiredError
  } else {
    const tempError = validateTemperature(form.temperature)
    if (tempError) errors.temperature = tempError
  }
  
  // 植物記録のバリデーション
  if (form.plantRecords) {
    Object.keys(form.plantRecords).forEach(plantId => {
      const plant = form.plantRecords[plantId]
      
      if (plant.height) {
        const heightError = validateHeight(plant.height)
        if (heightError) {
          if (!errors.plants) errors.plants = {}
          errors.plants[plantId] = { height: heightError }
        }
      }
      
      if (plant.image) {
        const imageError = validateImage(plant.image)
        if (imageError) {
          if (!errors.plants) errors.plants = {}
          if (!errors.plants[plantId]) errors.plants[plantId] = {}
          errors.plants[plantId].image = imageError
        }
      }
    })
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
}