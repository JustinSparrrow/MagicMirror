<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import MagicMirror from '../components/MagicMirror.vue'

const router = useRouter()
const userId = localStorage.getItem('user_id')
const username = localStorage.getItem('username') || '魔镜用户'

const baseUrl = import.meta.env.VITE_IMAGE_BASE_URL;

// 状态变量
const myStyles = ref([])      // 存储从后端获取的妆容列表
const activeMakeup = ref(null) // 当前选中的、正在试用的妆容数据
const isLoading = ref(false)

// 1. 获取历史妆容列表
const fetchStyles = async () => {
  try {
    const res = await api.get(`/makeup/my-styles/${userId}`)
    myStyles.value = res.data
  } catch (err) {
    console.error("加载历史库失败", err)
  }
}

// 2. 上传新妆容
const handleUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isLoading.value = true
  const formData = new FormData()
  formData.append('file', file)
  formData.append('user_id', userId)
  formData.append('name', `新妆容 ${myStyles.value.length + 1}`)

  try {
    const res = await api.post('/makeup/extract', formData)
    // 上传成功后，直接进入该妆容的试妆模式
    activeMakeup.value = res.data 
    // 同时静默刷新后台列表
    fetchStyles()
  } catch (err) {
    alert("提取失败，请确保图片清晰且包含面部")
  } finally {
    isLoading.value = false
  }
}

// 3. 删除妆容逻辑
const confirmDelete = async (styleId) => {
  if (!confirm("确定要删除这个妆容吗？这将物理回收存储空间。")) return
  
  try {
    await api.delete(`/makeup/delete/${styleId}?user_id=${userId}`)
    // 界面同步删除
    myStyles.value = myStyles.value.filter(s => s.id !== styleId)
    // 如果当前正在试用的正好是这一款，退出试妆
    if (activeMakeup.value?.id === styleId) activeMakeup.value = null
  } catch (err) {
    alert("删除失败")
  }
}

// 4. 退出登录
const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

onMounted(fetchStyles)
</script>

<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="logo-area">
        <h2 class="brand">MAGIC MIRROR</h2>
        <span class="user-tag">Hi, {{ username }}</span>
      </div>
      <div class="actions">
        <input type="file" @change="handleUpload" id="upload-input" hidden />
        <label for="upload-input" class="upload-btn" :class="{ 'disabled': isLoading }">
          {{ isLoading ? 'AI 提取中...' : '+ 提取新妆容' }}
        </label>
        <button @click="handleLogout" class="logout-link">退出</button>
      </div>
    </header>

    <main class="content-body">
      <!-- 【试妆模式】 -->
      <section v-if="activeMakeup" class="mirror-container">
        <div class="ar-toolbar">
          <button @click="activeMakeup = null" class="back-btn">← 返回我的库</button>
          <div class="current-info">
            正在试用：<strong>{{ activeMakeup.template_name }}</strong>
          </div>
        </div>
        <MagicMirror :makeupData="activeMakeup" />
      </section>

      <!-- 【画廊模式】 -->
      <section v-else class="library-container">
        <h3 class="title">我的妆容库 ({{ myStyles.length }})</h3>
        
        <!-- 空状态 -->
        <div v-if="myStyles.length === 0" class="empty-holder">
          <div class="empty-icon">✨</div>
          <p>这里空空如也，点击右上角上传一张妆容模板图吧</p>
        </div>

        <!-- 妆容网格 -->
        <div class="style-grid">
        <div v-for="style in myStyles" :key="style.id" class="style-card">
            <div class="card-media" @click="activeMakeup = style">
            <!-- 修正：baseUrl 直接拼接 style 里的路径 -->
            <img :src="baseUrl + style.lips_path" alt="lips preview" />
            <div class="overlay">点击开始试妆</div>
            </div>
            <div class="card-footer">
            <p class="name">{{ style.template_name }}</p>
            <button @click="confirmDelete(style.id)" class="del-btn" title="物理删除">✕</button>
            </div>
        </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.app-layout { background: #000; min-height: 100vh; color: #fff; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 40px; border-bottom: 1px solid #222; sticky: top; background: #000; z-index: 10; }
.brand { color: #4ade80; font-weight: 900; letter-spacing: 1px; }
.user-tag { font-size: 0.8rem; color: #666; margin-left: 10px; }

.upload-btn { background: #4ade80; color: #000; padding: 8px 20px; border-radius: 20px; font-weight: bold; cursor: pointer; transition: 0.3s; }
.upload-btn.disabled { opacity: 0.5; cursor: not-allowed; }
.logout-link { background: none; border: none; color: #444; margin-left: 15px; cursor: pointer; }

.content-body { padding: 30px; max-width: 1200px; margin: 0 auto; }

/* 画廊样式 */
.style-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 25px; }
.style-card { background: #111; border-radius: 16px; border: 1px solid #222; overflow: hidden; transition: 0.3s; }
.style-card:hover { transform: translateY(-5px); border-color: #4ade80; }

.card-media { height: 160px; background: #080808; display: flex; align-items: center; justify-content: center; cursor: pointer; position: relative; }
.card-media img { width: 120px; filter: drop-shadow(0 0 8px rgba(74, 222, 128, 0.2)); }
.overlay { position: absolute; inset: 0; background: rgba(74, 222, 128, 0.15); opacity: 0; display: flex; align-items: center; justify-content: center; font-weight: bold; transition: 0.3s; }
.card-media:hover .overlay { opacity: 1; }

.card-footer { padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; }
.name { font-size: 0.9rem; margin: 0; color: #ccc; }
.del-btn { background: none; border: none; color: #444; cursor: pointer; font-size: 1rem; }
.del-btn:hover { color: #ff4d4d; }

/* 试妆模式样式 */
.mirror-container { width: 640px; margin: 0 auto; animation: fadeIn 0.5s ease; }
.ar-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.back-btn { background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 6px 15px; border-radius: 8px; cursor: pointer; }
.current-info { font-size: 0.9rem; color: #888; }
.current-info strong { color: #4ade80; }

.empty-holder { text-align: center; padding-top: 100px; color: #333; }
.empty-icon { font-size: 4rem; margin-bottom: 20px; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>