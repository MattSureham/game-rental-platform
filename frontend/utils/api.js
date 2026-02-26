// API 服务基础配置
const BASE_URL = 'http://localhost:8000/api'

// 请求拦截器
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('user')
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          })
          reject(new Error('Unauthorized'))
        } else {
          uni.showToast({
            title: res.data.detail || '请求失败',
            icon: 'none'
          })
          reject(new Error(res.data.detail || '请求失败'))
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// API 方法
export const api = {
  // 认证
  auth: {
    login: (code) => request({
      url: '/auth/login',
      method: 'POST',
      data: { code }
    }),
    getProfile: () => request({
      url: '/auth/profile',
      method: 'GET'
    }),
    updateProfile: (data) => request({
      url: '/auth/profile',
      method: 'PUT',
      data
    }),
    updateWechatId: (wechat_id) => request({
      url: '/auth/wechat-id',
      method: 'PUT',
      data: { wechat_id }
    })
  },
  
  // 商品
  products: {
    list: (params) => request({
      url: '/products',
      method: 'GET',
      data: params
    }),
    myList: () => request({
      url: '/products/my',
      method: 'GET'
    }),
    detail: (id) => request({
      url: `/products/${id}`,
      method: 'GET'
    }),
    create: (data) => request({
      url: '/products',
      method: 'POST',
      data
    }),
    update: (id, data) => request({
      url: `/products/${id}`,
      method: 'PUT',
      data
    }),
    delete: (id) => request({
      url: `/products/${id}`,
      method: 'DELETE'
    }),
    categories: () => request({
      url: '/products/categories',
      method: 'GET'
    })
  },
  
  // 订单
  orders: {
    create: (data) => request({
      url: '/orders',
      method: 'POST',
      data
    }),
    list: (params) => request({
      url: '/orders',
      method: 'GET',
      data: params
    }),
    renting: () => request({
      url: '/orders/renting',
      method: 'GET'
    }),
    lending: () => request({
      url: '/orders/lending',
      method: 'GET'
    }),
    detail: (id) => request({
      url: `/orders/${id}`,
      method: 'GET'
    }),
    contact: (id) => request({
      url: `/orders/${id}/contact`,
      method: 'GET'
    }),
    pay: (id) => request({
      url: `/orders/${id}/pay`,
      method: 'POST'
    }),
    return: (id, remark) => request({
      url: `/orders/${id}/return`,
      method: 'POST',
      data: { remark }
    }),
    confirm: (id, remark) => request({
      url: `/orders/${id}/confirm`,
      method: 'POST',
      data: { remark }
    }),
    dispute: (id, reason, evidence) => request({
      url: `/orders/${id}/dispute`,
      method: 'POST',
      data: { reason, evidence }
    }),
    cancel: (id) => request({
      url: `/orders/${id}/cancel`,
      method: 'POST'
    })
  },
  
  // 钱包
  wallet: {
    balance: () => request({
      url: '/wallet/balance',
      method: 'GET'
    }),
    logs: (params) => request({
      url: '/wallet/logs',
      method: 'GET',
      data: params
    }),
    recharge: (amount) => request({
      url: '/wallet/recharge',
      method: 'POST',
      data: { amount }
    }),
    withdraw: (amount) => request({
      url: '/wallet/withdraw',
      method: 'POST',
      data: { amount }
    })
  }
}

export default api
