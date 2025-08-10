// API呼び出しとエラーハンドリングの共通化
export const useApi = () => {
  const config = useRuntimeConfig()
  // normalize base to avoid double slashes and repeated /api
  let base = (config.public.apiBase || '').replace(/\/+$/, '')
  // collapse trailing repeated /api segments (e.g. "/api/api" -> "/api")
  base = base.replace(/(?:\/api)+$/, '/api')
  
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
      // 与えられたurlを正規化し、`/api` の二重付与を防止
      const raw = `${url}`
      // 絶対URLはそのまま呼び出す
      if (/^https?:\/\//i.test(raw)) {
        const response = await $fetch(raw, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers
          }
        })
        return { data: response, error: null }
      }

      // 先頭スラッシュ付与
      let path = raw.startsWith('/') ? raw : `/${raw}`
      // 連続スラッシュを1つに（パス部分のみ）
      path = path.replace(/\/{2,}/g, '/')
      // パス先頭の "/api" をすべて取り除く（base 側で付与済みのため）
      path = path.replace(/^\/(?:api)(?=\/|$)/, '')
      while (path.startsWith('/api/')) {
        path = path.replace(/^\/api\//, '/')
      }
      // 再度、先頭スラッシュを保証
      if (!path.startsWith('/')) {
        path = `/${path}`
      }
      // base が空の場合はデフォルトで /api を使用
      if (!base) {
        base = '/api'
      }

      // 結合し、/api の重複を安全に縮約
      let finalUrl = `${base}${path}`
      finalUrl = finalUrl.replace(/(\/api){2,}/g, '/api')

      // 開発時のデバッグログ（ブラウザのみ）
      if (typeof window !== 'undefined' && !(process && process.env && process.env.NODE_ENV === 'production')) {
        // eslint-disable-next-line no-console
        console.debug('[useApi] request', { base, raw, path, finalUrl })
      }

      const response = await $fetch(finalUrl, {
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
      
      const response = await $fetch(`${base}/upload/image`, {
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