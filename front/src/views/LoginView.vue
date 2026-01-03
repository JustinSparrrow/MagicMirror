<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>{{ isLogin ? '魔镜登录' : '新用户注册' }}</h2>
      
      <form @submit.prevent="handleSubmit">
        <input v-model="form.username" type="text" placeholder="用户名" required />
        <input v-model="form.password" type="password" placeholder="密码" required />
        
        <button type="submit" :disabled="loading">
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <p @click="isLogin = !isLogin">
        {{ isLogin ? '没有账号？立即注册' : '已有账号？直接登录' }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()
const isLogin = ref(true)
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const handleSubmit = async () => {
  loading.value = true
  const path = isLogin.value ? '/auth/login' : '/auth/register'
  
  const formData = new FormData()
  formData.append('username', form.username)
  formData.append('password', form.password)

  try {
    const res = await api.post(path, formData)
    if (isLogin.value) {
      // 登录成功：持久化 Token 和 UserID
      localStorage.setItem('token', res.data.access_token)
      localStorage.setItem('user_id', res.data.user_id)
      router.push('/') // 跳转到主页
    } else {
      alert('注册成功，请登录')
      isLogin.value = true
    }
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container { height: 100vh; display: flex; align-items: center; justify-content: center; background: #000; }
.auth-card { background: #1a1a1a; padding: 40px; border-radius: 20px; width: 320px; text-align: center; }
input { width: 100%; padding: 12px; margin: 10px 0; background: #333; border: none; color: white; border-radius: 8px; box-sizing: border-box; }
button { width: 100%; padding: 12px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; }
p { color: #888; font-size: 0.9rem; margin-top: 20px; cursor: pointer; }
</style>

