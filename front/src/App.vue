<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import VideoLibrary from './components/VideoLibrary.vue'
import VideoPlayer from './components/VideoPlayer.vue'
import type { Video, AnalysisData } from './types'

// API基础URL
const API_BASE_URL = 'http://localhost:8000'

// 响应式数据
const videos = ref<Video[]>([])
const selectedVideo = ref<Video | null>(null)
const analysisData = ref<AnalysisData | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const currentView = ref<'library' | 'player'>('library')

// 获取视频列表
const fetchVideos = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await axios.get(`${API_BASE_URL}/api/videos`)
    videos.value = response.data.videos
  } catch (err) {
    error.value = '获取视频列表失败'
    console.error('获取视频列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 获取视频分析数据
const fetchAnalysis = async (videoId: string) => {
  try {
    loading.value = true
    error.value = null
    const response = await axios.get(`${API_BASE_URL}/api/analysis?video=${videoId}`)
    analysisData.value = response.data
  } catch (err) {
    error.value = '获取分析数据失败'
    console.error('获取分析数据失败:', err)
  } finally {
    loading.value = false
  }
}

// 选择视频
const selectVideo = (video: Video) => {
  selectedVideo.value = video
  if (video.has_analysis) {
    fetchAnalysis(video.id)
  } else {
    analysisData.value = null
  }
  currentView.value = 'player'
}

// 返回视频库
const backToLibrary = () => {
  currentView.value = 'library'
  selectedVideo.value = null
  analysisData.value = null
}

// 组件挂载时获取视频列表
onMounted(() => {
  fetchVideos()
})
</script>

<template>
  <div id="app">
    <header class="ph-header">
      <div class="header-content">
        <div class="logo" @click="backToLibrary">
          <span class="white">Ready2</span><span class="orange">Masturbate</span>
        </div>
        
        <div class="search-bar">
          <input type="text" placeholder="Search videos..." />
          <button class="search-btn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </button>
        </div>

        <div class="header-actions">
          <button
            @click="fetchVideos"
            :disabled="loading"
            class="action-link"
            title="Refresh"
          >
            Refresh
          </button>
        </div>
      </div>
      
      <nav class="sub-nav">
        <div class="nav-content">
          <a href="#" class="active">Home</a>
          <a href="#">Videos</a>
          <a href="#">Categories</a>
          <a href="#">Live</a>
          <a href="#">Community</a>
          <a href="#">Photos</a>
        </div>
      </nav>
    </header>

    <main class="ph-main">
      <div class="content-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="spinner"></div>
        </div>

        <!-- 错误信息 -->
        <div v-if="error" class="error-alert">
          <p>{{ error }}</p>
          <button @click="error = null">Dismiss</button>
        </div>

        <!-- 视频库视图 -->
        <VideoLibrary 
          v-if="currentView === 'library' && !loading"
          :videos="videos"
          @select-video="selectVideo"
        />

        <!-- 视频播放器视图 -->
        <div v-if="currentView === 'player' && selectedVideo && !loading" class="player-view">
          <div class="back-nav">
            <button @click="backToLibrary" class="back-link">
              &lt; Back to Videos
            </button>
          </div>
          <VideoPlayer
            :video="selectedVideo"
            :analysis-data="analysisData"
            :all-videos="videos"
            @select-video="selectVideo"
          />
        </div>
      </div>
    </main>

    <footer class="ph-footer">
      <div class="footer-content">
        <p class="copyright">&copy; 2025 Ready2Masturbate. All rights reserved.</p>
        <div class="footer-links">
          <a href="#">Terms</a>
          <a href="#">Privacy</a>
          <a href="#">DMCA</a>
          <a href="#">2257</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Header Styles */
.ph-header {
  background-color: var(--color-bg-primary);
  border-bottom: 2px solid var(--color-accent);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 40px;
  max-width: 1400px;
  margin: 0 auto;
  height: 70px;
}

.logo {
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
  letter-spacing: -1px;
  user-select: none;
}

.logo .white {
  background: white;
  color: black;
  padding: 2px 5px;
  border-radius: 3px;
  margin-right: 2px;
}

.logo .orange {
  background: var(--color-accent);
  color: black;
  padding: 2px 5px;
  border-radius: 3px;
}

.search-bar {
  flex: 1;
  max-width: 600px;
  margin: 0 40px;
  display: flex;
}

.search-bar input {
  width: 100%;
  padding: 10px 15px;
  background: #333;
  border: 1px solid #333;
  color: white;
  font-size: 14px;
  border-radius: 2px 0 0 2px;
}

.search-bar input:focus {
  background: white;
  color: black;
  outline: none;
}

.search-btn {
  background: #333;
  border: 1px solid #333;
  color: #999;
  padding: 0 15px;
  border-radius: 0 2px 2px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  color: white;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-link {
  color: var(--color-text-secondary);
  font-weight: bold;
  font-size: 14px;
}

.action-link:hover {
  color: white;
}

.btn-signup {
  background: var(--color-accent);
  color: black;
  padding: 8px 15px;
  border-radius: 3px;
  font-weight: bold;
  font-size: 14px;
}

.btn-signup:hover {
  background: var(--color-accent-hover);
}

.sub-nav {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid #333;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  gap: 30px;
  height: 40px;
  align-items: center;
}

.nav-content a {
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: bold;
  height: 100%;
  display: flex;
  align-items: center;
  border-bottom: 3px solid transparent;
}

.nav-content a:hover,
.nav-content a.active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

/* Main Content Styles */
.ph-main {
  flex: 1;
  background-color: var(--color-bg-primary);
  padding: 30px 0;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 50px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #333;
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-alert {
  background: #300;
  border: 1px solid #600;
  color: #fcc;
  padding: 15px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.back-nav {
  margin-bottom: 20px;
}

.back-link {
  color: var(--color-text-secondary);
  font-size: 14px;
  display: flex;
  align-items: center;
}

.back-link:hover {
  color: var(--color-accent);
}

/* Footer Styles */
.ph-footer {
  background: var(--color-bg-secondary);
  padding: 40px 0;
  border-top: 1px solid #333;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-links a {
  color: var(--color-text-secondary);
}

.footer-links a:hover {
  color: var(--color-accent);
}
</style>
