import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const userName = computed(() => user.value?.full_name || user.value?.email || 'User')

  // Actions
  const login = async (credentials) => {
    try {
      const response = await axios.post('/api/v1/auth/login', credentials)
      const { access_token, refresh_token, user: userData } = response.data

      // Store tokens
      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData

      // Store in localStorage
      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      localStorage.setItem('user', JSON.stringify(userData))

      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        message: error.response?.data?.error?.message || 'Login failed'
      }
    }
  }

  const logout = async () => {
    try {
      // Clear state
      user.value = null
      token.value = null
      refreshToken.value = null

      // Clear localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')

      // Clear authorization header
      delete axios.defaults.headers.common['Authorization']

      return { success: true }
    } catch (error) {
      console.error('Logout error:', error)
      return { success: false }
    }
  }

  const checkAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
    }
  }

  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      const response = await axios.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken.value
      })

      const { access_token, refresh_token: newRefreshToken, user: userData } = response.data

      // Update tokens
      token.value = access_token
      refreshToken.value = newRefreshToken
      user.value = userData

      // Update localStorage
      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', newRefreshToken)
      localStorage.setItem('user', JSON.stringify(userData))

      // Update authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      return { success: true }
    } catch (error) {
      console.error('Token refresh error:', error)
      // If refresh fails, logout user
      await logout()
      return { success: false }
    }
  }

  return {
    // State
    user,
    token,
    refreshToken,
    // Getters
    isAuthenticated,
    userRole,
    userName,
    // Actions
    login,
    logout,
    checkAuth,
    refreshAccessToken
  }
})
