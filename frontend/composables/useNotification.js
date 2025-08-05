// 統一された通知システム
export const useNotification = () => {
  const notifications = ref([])
  
  const addNotification = (message, type = 'info', duration = 5000) => {
    const id = Date.now()
    const notification = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      duration
    }
    
    notifications.value.push(notification)
    
    // 自動削除
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
    
    return id
  }
  
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  const clearAll = () => {
    notifications.value = []
  }
  
  // 便利メソッド
  const showSuccess = (message, duration = 3000) => {
    return addNotification(message, 'success', duration)
  }
  
  const showError = (message, duration = 5000) => {
    return addNotification(message, 'error', duration)
  }
  
  const showWarning = (message, duration = 4000) => {
    return addNotification(message, 'warning', duration)
  }
  
  const showInfo = (message, duration = 3000) => {
    return addNotification(message, 'info', duration)
  }
  
  return {
    notifications: readonly(notifications),
    addNotification,
    removeNotification,
    clearAll,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}