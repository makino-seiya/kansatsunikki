// API呼び出しとエラーハンドリングの共通化
export const useApi = () => {
  const config = useRuntimeConfig()
  
  // 統一されたエラーハンドリング
  const handleApiError = (error) => {
    console.error('API Error:', error)
    
    // エラーの詳細をログ出力
    if (error.data) {
      console.error('Error data:', error.data)
    }
    if (error.status) {
      console.error('Error status:', error.status)
    }
    if (error.message) {
      console.error('Error message:', error.message)
    }
    
    if (error.data?.detail) {
      return error.data.detail
    }
    
    if (error.status === 404) {
      return 'データが見つかりません'
    }
    
    if (error.status === 400) {
      return '入力データに問題があります'
    }
    
    if (error.status === 500) {
      return 'サーバーエラーが発生しました'
    }
    
    if (error.status === 0 || !error.status) {
      return 'ネットワークエラーが発生しました'
    }
    
    return '予期しないエラーが発生しました'
  }
  
  // 統一されたAPI呼び出し関数
  const apiCall = async (url, options = {}) => {
    try {
      const response = await $fetch(`${config.public.apiBase}${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      })
      return { data: response, error: null }
    } catch (error) {
      return { data: null, error: handleApiError(error) }
    }
  }
  
  // 画像アップロード専用関数
  const uploadImage = async (file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await $fetch(`${config.public.apiBase}/api/upload/image`, {
        method: 'POST',
        body: formData
      })
      return { data: response, error: null }
    } catch (error) {
      return { data: null, error: handleApiError(error) }
    }
  }
  
  return {
    apiCall,
    uploadImage,
    handleApiError
  }
}