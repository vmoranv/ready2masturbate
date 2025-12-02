<script setup lang="ts">
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'
import type { Video, AnalysisData, FrameData } from '../types'
import CustomProgressBar from './CustomProgressBar.vue'

interface Props {
  video: Video
  analysisData: AnalysisData | null
  allVideos?: Video[]  // 添加可选标记
}

interface Emits {
  (e: 'select-video', video: Video): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// 响应式数据
const videoRef = ref<HTMLVideoElement>()
const currentTime = ref(0)
const duration = ref(0)
const isPlaying = ref(false)
const volume = ref(1)
const showControls = ref(true)
let controlsTimeout: number | null = null

// 计算属性
const hasAnalysis = computed(() => props.analysisData !== null)

// 获取推荐视频列表（排除当前播放的视频）
const recommendedVideos = computed(() => {
  if (!props.allVideos || !Array.isArray(props.allVideos)) {
    return []
  }
  return props.allVideos
    .filter(video => video.has_analysis && video.id !== props.video.id)
    .slice(0, 5) // 只显示前5个推荐视频
})

// 处理推荐视频点击
const selectRecommendedVideo = (video: Video) => {
  emit('select-video', video)
}

// Chart Data (Simplified for dark theme)
const chartData = computed(() => {
  if (!hasAnalysis.value || !props.analysisData?.chart_data) {
    return { labels: [], datasets: [] }
  }

  const frames = props.analysisData.chart_data
  const labels = frames.map(frame => frame.timestamp)
  const scores = frames.map(frame => frame.nsfw_score)

  return {
    labels,
    datasets: [
      {
        label: 'NSFW Score',
        data: scores,
        borderColor: '#ffa31a',
        backgroundColor: 'rgba(255, 163, 26, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointBackgroundColor: '#ffa31a'
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: false },
    tooltip: {
      enabled: false, // Disable default tooltip
      external: (context: any) => {
        // Custom tooltip implementation
        const tooltipEl = document.getElementById('chartjs-tooltip')

        if (!tooltipEl || context.tooltip.opacity === 0) {
          if (tooltipEl) tooltipEl.style.opacity = '0'
          return
        }

        if (context.tooltip.body) {
          const dataIndex = context.tooltip.dataPoints[0].dataIndex
          const frameData = props.analysisData?.chart_data?.[dataIndex]
          
          if (frameData) {
            // Set tooltip content
            const titleEl = document.getElementById('tooltip-title')
            const descEl = document.getElementById('tooltip-desc')
            const tagsEl = document.getElementById('tooltip-tags')
            const imgEl = document.getElementById('tooltip-img') as HTMLImageElement
            const scoreEl = document.getElementById('tooltip-score')
            
            if (titleEl) titleEl.innerHTML = `Time: ${frameData.timestamp}`
            if (descEl) {
              const description = frameData.description || 'No description available'
              descEl.innerHTML = description
            }
            if (scoreEl) scoreEl.innerHTML = `NSFW Score: ${frameData.nsfw_score.toFixed(1)}%`
            
            // Display tags
            if (tagsEl && frameData.tags && frameData.tags.length > 0) {
              const tagsHtml = frameData.tags.map((tag: string) =>
                `<span class="tag">${tag}</span>`
              ).join('')
              tagsEl.innerHTML = tagsHtml
              tagsEl.style.display = 'flex'
            } else if (tagsEl) {
              tagsEl.style.display = 'none'
            }
            
            // Set thumbnail image
            if (imgEl) {
              const videoId = props.video.id
              imgEl.src = `http://localhost:8000/api/thumbnail?id=${videoId}&frame=${frameData.filename}`
              imgEl.onerror = () => {
                imgEl.style.display = 'none'
              }
              imgEl.onload = () => {
                imgEl.style.display = 'block'
              }
            }
            
            // Position tooltip
            const position = context.chart.canvas.getBoundingClientRect()
            tooltipEl.style.opacity = '1'
            tooltipEl.style.left = position.left + window.pageXOffset + context.tooltip.caretX + 'px'
            tooltipEl.style.top = position.top + window.pageYOffset + context.tooltip.caretY - 100 + 'px'
          }
        }
      }
    }
  },
  scales: {
    y: {
      display: false,
      min: 0,
      max: 100
    },
    x: {
      display: false
    }
  },
  interaction: {
    mode: 'nearest' as const,
    axis: 'x' as const,
    intersect: false
  },
  onClick: (event: any, elements: any) => {
    if (elements.length > 0) {
      const dataIndex = elements[0].index
      const frameData = props.analysisData?.chart_data?.[dataIndex]
      
      if (frameData) {
        // Convert timestamp to seconds
        const timeToSeconds = (timestamp: string) => {
          const parts = timestamp.split(':').map(Number)
          return (parts[0] || 0) * 3600 + (parts[1] || 0) * 60 + (parts[2] || 0)
        }
        
        const targetTime = timeToSeconds(frameData.timestamp)
        onSeek(targetTime)
      }
    }
  }
}))

// Video Control Methods
const togglePlay = () => {
  if (!videoRef.value) return
  if (isPlaying.value) {
    videoRef.value.pause()
  } else {
    videoRef.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const handleTimeUpdate = () => {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime
  }
}

const handleLoadedMetadata = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration
  }
}

const onSeek = (time: number) => {
  if (videoRef.value) {
    videoRef.value.currentTime = time
    currentTime.value = time
  }
}

const onSeeking = (time: number) => {
  // Optional: Update UI while dragging without setting video time yet if desired
  // For now, we can just update the current time display or seek immediately
  if (videoRef.value) {
      videoRef.value.currentTime = time
      currentTime.value = time
  }
}

// Controls visibility
const showControlsOverlay = () => {
  showControls.value = true
  if (controlsTimeout) clearTimeout(controlsTimeout)
  controlsTimeout = setTimeout(() => {
    if (isPlaying.value) {
      showControls.value = false
    }
  }, 3000)
}

// Format time helper
const formatTime = (seconds: number) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m}:${s.toString().padStart(2, '0')}`
}

onMounted(() => {
  nextTick(() => {
    if (videoRef.value) {
      videoRef.value.addEventListener('timeupdate', handleTimeUpdate)
      videoRef.value.addEventListener('loadedmetadata', handleLoadedMetadata)
    }
  })
})

onUnmounted(() => {
  if (controlsTimeout) clearTimeout(controlsTimeout)
})
</script>

<template>
  <div class="video-player-page">
    <div class="main-content">
      <!-- Video Player Container -->
      <div 
        class="player-container"
        @mousemove="showControlsOverlay"
        @mouseleave="showControls = false"
      >
        <video
          ref="videoRef"
          :src="`http://localhost:8000/api/video-file?path=${encodeURIComponent(video.video_path)}`"
          @play="isPlaying = true"
          @pause="isPlaying = false"
          @click="togglePlay"
          class="video-element"
        ></video>

        <!-- Controls Overlay -->
        <div class="controls-overlay" :class="{ 'visible': showControls || !isPlaying }">
          <CustomProgressBar
            :current-time="currentTime"
            :duration="duration"
            :analysis-data="analysisData"
            @seek="onSeek"
            @seeking="onSeeking"
          />
          
          <div class="controls-bar">
            <div class="left-controls">
              <button @click="togglePlay" class="control-btn play-btn">
                {{ isPlaying ? '❚❚' : '▶' }}
              </button>
              <span class="time-display">
                {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
              </span>
            </div>
            
            <div class="right-controls">
              <button class="control-btn">HD</button>
              <button class="control-btn">⛶</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Video Info & Actions -->
      <div class="video-info-section">
        <div class="video-header">
          <h1 class="video-title">{{ video.filename }}</h1>
          <div class="video-actions">
            <button class="action-btn like">
              <span class="icon">👍</span>
            </button>
            <button class="action-btn dislike">
              <span class="icon">👎</span>
            </button>
            <button class="action-btn add">
              <span class="icon">+</span> Add to
            </button>
            <button class="action-btn share">
              <span class="icon">↗</span> Share
            </button>
          </div>
        </div>

        <div class="video-meta-row">
          <div class="upload-info">
            Local video
          </div>
        </div>
      </div>

      <!-- Analysis Chart (Subtle) -->
      <div v-if="hasAnalysis" class="analysis-widget">
        <h3>Content Intensity Analysis</h3>
        <div class="chart-wrapper">
          <Line :data="chartData" :options="chartOptions" />
        </div>
      </div>
    </div>

    <!-- Sidebar (Recommendations) -->
    <div class="sidebar">
      <div class="ad-placeholder">
        Advertisement
      </div>
      <div class="recommendations">
        <h3>Up Next</h3>
        <!-- Real recommendations list -->
        <div
          v-for="video in recommendedVideos"
          :key="video.id"
          class="rec-item"
          @click="selectRecommendedVideo(video)"
        >
          <div class="rec-thumb">
            <img
              v-if="video.has_analysis"
              :src="`http://localhost:8000/api/thumbnail?id=${video.id}`"
              class="rec-thumb-img"
              @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
            />
            <div class="rec-thumb-placeholder"></div>
          </div>
          <div class="rec-info">
            <div class="rec-title" :title="video.filename">{{ video.filename }}</div>
            <div class="rec-meta">
              <span v-if="video.average_nsfw_score" class="rec-rating">
                {{ (video.average_nsfw_score * 100).toFixed(0) }}% match
              </span>
              <span v-else>Analyzed</span>
            </div>
          </div>
        </div>
        
        <!-- Fallback if no recommendations -->
        <div v-if="recommendedVideos.length === 0" class="no-recommendations">
          <p>No other analyzed videos available</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Custom Tooltip for Chart -->
  <div id="chartjs-tooltip" class="chart-tooltip">
    <div class="tooltip-content">
      <img id="tooltip-img" class="tooltip-image" />
      <div class="tooltip-info">
        <div id="tooltip-title" class="tooltip-title"></div>
        <div id="tooltip-score" class="tooltip-score"></div>
        <div id="tooltip-tags" class="tooltip-tags"></div>
        <div id="tooltip-desc" class="tooltip-description"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-player-page {
  display: flex;
  gap: 20px;
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
}

.main-content {
  flex: 1;
  min-width: 0; /* Prevent flex overflow */
}

.sidebar {
  width: 350px;
  flex-shrink: 0;
}

/* Player Styles */
.player-container {
  position: relative;
  width: 100%;
  background: black;
  aspect-ratio: 16/9;
  margin-bottom: 20px;
  overflow: hidden;
}

.video-element {
  width: 100%;
  height: 100%;
  display: block;
}

.controls-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  padding: 10px 15px;
  opacity: 0;
  transition: opacity 0.3s;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.controls-overlay.visible {
  opacity: 1;
}

.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-controls, .right-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.control-btn {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.control-btn:hover {
  opacity: 1;
}

.play-btn {
  font-size: 20px;
  width: 30px;
}

.time-display {
  color: white;
  font-size: 13px;
  font-family: Arial, sans-serif;
}

/* Info Section */
.video-info-section {
  margin-bottom: 20px;
  border-bottom: 1px solid #333;
  padding-bottom: 20px;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.video-title {
  font-size: 20px;
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.3;
}

.video-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: #333;
  border: none;
  color: var(--color-text-primary);
  padding: 8px 15px;
  border-radius: 2px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn:hover {
  background: #444;
}

.action-btn.like {
  border-bottom: 2px solid #28a745;
}

.video-meta-row {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.uploader-link {
  color: var(--color-text-primary);
  font-weight: bold;
}

.uploader-link:hover {
  color: var(--color-accent);
}

/* Analysis Widget */
.analysis-widget {
  background: #1b1b1b;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.analysis-widget h3 {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
  text-transform: uppercase;
}

.chart-wrapper {
  height: 150px;
}

/* Sidebar */
.ad-placeholder {
  background: #222;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #444;
  margin-bottom: 20px;
}

.recommendations h3 {
  font-size: 16px;
  color: var(--color-text-primary);
  margin-bottom: 15px;
}

.rec-item {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  cursor: pointer;
}

.rec-thumb {
  width: 168px;
  height: 94px;
  background: #333;
  position: relative;
  overflow: hidden;
}

.rec-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rec-thumb-placeholder {
  width: 100%;
  height: 100%;
  background: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 24px;
}

.rec-thumb-img[style*="display: none"] + .rec-thumb-placeholder {
  display: flex;
}

.rec-thumb-img:not([style*="display: none"]) + .rec-thumb-placeholder {
  display: none;
}

.rec-info {
  flex: 1;
}

.rec-title {
  font-size: 13px;
  color: var(--color-text-primary);
  margin-bottom: 5px;
  line-height: 1.3;
  font-weight: bold;
}

.rec-meta {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.rec-rating {
  background: rgba(255, 163, 26, 0.2);
  color: #ffa31a;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: bold;
}

.no-recommendations {
  text-align: center;
  padding: 20px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

/* Chart Tooltip Styles */
.chart-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid #333;
  border-radius: 8px;
  padding: 12px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 1000;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.tooltip-content {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.tooltip-image {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  background: #333;
  display: none;
}

.tooltip-info {
  flex: 1;
  min-width: 0;
}

.tooltip-title {
  font-size: 13px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tooltip-score {
  font-size: 12px;
  color: var(--color-accent);
  margin-bottom: 6px;
  font-weight: bold;
}

.tooltip-tags {
  display: none;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}

.tag {
  font-size: 10px;
  background: rgba(255, 163, 26, 0.2);
  color: #ffa31a;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid rgba(255, 163, 26, 0.3);
  white-space: nowrap;
}

.tooltip-description {
  font-size: 11px;
  color: #ccc;
  line-height: 1.3;
  max-height: 60px;
  overflow-y: auto;
  word-wrap: break-word;
}

/* Chart cursor pointer */
.chart-wrapper {
  cursor: pointer;
}

.chart-wrapper:hover {
  opacity: 0.9;
}
</style>