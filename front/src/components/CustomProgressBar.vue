<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { AnalysisData, FrameData } from '../types'

const props = defineProps<{
  currentTime: number
  duration: number
  buffered?: TimeRanges
  analysisData?: AnalysisData | null
}>()

const emit = defineEmits<{
  (e: 'seek', time: number): void
  (e: 'seeking', time: number): void
}>()

const progressBarRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const hoverTime = ref<number | null>(null)
const hoverPosition = ref(0)

// Calculate progress percentage
const progressPercent = computed(() => {
  if (!props.duration) return 0
  return (props.currentTime / props.duration) * 100
})

// Calculate intensity segments from analysis data
const intensitySegments = computed(() => {
  if (!props.analysisData?.chart_data) return []
  
  const frames = props.analysisData.chart_data
  const segments: Array<{ start: number; end: number; intensity: number; color: string }> = []
  
  for (let i = 0; i < frames.length - 1; i++) {
    const frame = frames[i]
    const nextFrame = frames[i + 1]
    
    // Convert timestamp to seconds (assuming format like "00:01:30")
    const timeToSeconds = (timestamp: string) => {
      const parts = timestamp.split(':').map(Number)
      return (parts[0] || 0) * 3600 + (parts[1] || 0) * 60 + (parts[2] || 0)
    }
    
    const startTime = timeToSeconds(frame?.timestamp || '')
    const endTime = timeToSeconds(nextFrame?.timestamp || '')
    const intensity = (frame?.nsfw_score || 0) / 100 // Normalize to 0-1
    
    // Color based on intensity
    let color = '#4CAF50' // Green for low intensity
    if (intensity > 0.7) {
      color = '#F44336' // Red for high intensity
    } else if (intensity > 0.4) {
      color = '#FF9800' // Orange for medium intensity
    } else if (intensity > 0.2) {
      color = '#FFEB3B' // Yellow for low-medium intensity
    }
    
    segments.push({
      start: (startTime / props.duration) * 100,
      end: (endTime / props.duration) * 100,
      intensity,
      color
    })
  }
  
  return segments
})

// Get current intensity at current time
const currentIntensity = computed(() => {
  if (!props.analysisData?.chart_data || !props.currentTime) return 0
  
  const frames = props.analysisData.chart_data
  const currentFrame = frames.find(frame => {
    const timeToSeconds = (timestamp: string) => {
      const parts = timestamp.split(':').map(Number)
      return (parts[0] || 0) * 3600 + (parts[1] || 0) * 60 + (parts[2] || 0)
    }
    return timeToSeconds(frame?.timestamp || '') >= props.currentTime
  })
  
  return currentFrame ? currentFrame.nsfw_score / 100 : 0
})

// Format time helper
const formatTime = (seconds: number) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }
  return `${m}:${s.toString().padStart(2, '0')}`
}

// Handle mouse move over progress bar
const handleMouseMove = (e: MouseEvent) => {
  if (!progressBarRef.value) return
  
  const rect = progressBarRef.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width))
  const percentage = x / rect.width
  
  hoverPosition.value = x
  hoverTime.value = percentage * props.duration
  
  if (isDragging.value) {
    emit('seeking', hoverTime.value)
  }
}

// Handle mouse down (start dragging)
const handleMouseDown = (e: MouseEvent) => {
  isDragging.value = true
  handleMouseMove(e)
  document.addEventListener('mousemove', handleWindowMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// Handle window mouse move (while dragging)
const handleWindowMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !progressBarRef.value) return
  
  const rect = progressBarRef.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width))
  const percentage = x / rect.width
  const time = percentage * props.duration
  
  emit('seeking', time)
}

// Handle mouse up (end dragging)
const handleMouseUp = (e: MouseEvent) => {
  if (isDragging.value) {
    if (progressBarRef.value) {
        const rect = progressBarRef.value.getBoundingClientRect()
        const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width))
        const percentage = x / rect.width
        const time = percentage * props.duration
        emit('seek', time)
    }
    isDragging.value = false
    document.removeEventListener('mousemove', handleWindowMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
}

// Handle mouse leave
const handleMouseLeave = () => {
  if (!isDragging.value) {
    hoverTime.value = null
  }
}
</script>

<template>
  <div 
    class="progress-container"
    ref="progressBarRef"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    @mousedown="handleMouseDown"
  >
    <!-- Background Track -->
    <div class="progress-track">
      <!-- Intensity Segments (Analysis Data) -->
      <div
        v-for="(segment, index) in intensitySegments"
        :key="index"
        class="intensity-segment"
        :style="{
          left: `${segment.start}%`,
          width: `${segment.end - segment.start}%`,
          backgroundColor: segment.color,
          opacity: 0.3 + (segment.intensity * 0.7)
        }"
      />
      
      <!-- Progress Fill -->
      <div
        class="progress-fill"
        :style="{
          width: `${progressPercent}%`,
          backgroundColor: currentIntensity > 0.7 ? '#F44336' :
                         currentIntensity > 0.4 ? '#FF9800' :
                         currentIntensity > 0.2 ? '#FFEB3B' : '#4CAF50'
        }"
      >
        <div class="progress-handle"></div>
      </div>
      
      <!-- Hover Preview -->
      <div
        v-if="hoverTime !== null"
        class="hover-preview"
        :style="{ left: `${hoverPosition}px` }"
      >
        <div class="preview-line"></div>
        <div class="time-tooltip">{{ formatTime(hoverTime) }}</div>
      </div>
    </div>
    
    <!-- Intensity Indicator -->
    <div v-if="analysisData" class="intensity-indicator">
      <div class="intensity-label">Intensity:</div>
      <div
        class="intensity-bar"
        :style="{
          width: `${currentIntensity * 100}%`,
          backgroundColor: currentIntensity > 0.7 ? '#F44336' :
                         currentIntensity > 0.4 ? '#FF9800' :
                         currentIntensity > 0.2 ? '#FFEB3B' : '#4CAF50'
        }"
      />
      <div class="intensity-value">{{ Math.round(currentIntensity * 100) }}%</div>
    </div>
  </div>
</template>

<style scoped>
.progress-container {
  height: 15px; /* Hit area height */
  width: 100%;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  user-select: none;
}

.progress-track {
  height: 3px;
  width: 100%;
  background: rgba(255, 255, 255, 0.2);
  position: relative;
  transition: height 0.1s ease;
}

.progress-container:hover .progress-track {
  height: 5px;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-accent);
  position: relative;
  width: 0%;
}

.progress-handle {
  width: 12px;
  height: 12px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%) scale(0);
  transition: transform 0.1s ease;
  box-shadow: 0 0 4px rgba(0,0,0,0.5);
}

.progress-container:hover .progress-handle,
.progress-container:active .progress-handle {
  transform: translateY(-50%) scale(1);
}

.hover-preview {
  position: absolute;
  top: 0;
  bottom: 0;
  pointer-events: none;
  transform: translateX(-50%);
}

.preview-line {
  width: 1px;
  height: 100%;
  background: rgba(255, 255, 255, 0.5);
  margin: 0 auto;
}

.time-tooltip {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  white-space: nowrap;
}

.intensity-segment {
  position: absolute;
  top: 0;
  height: 100%;
  transition: opacity 0.2s ease;
}

.progress-container:hover .intensity-segment {
  opacity: 0.8 !important;
}

.intensity-indicator {
  display: flex;
  align-items: center;
  margin-top: 8px;
  gap: 10px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.intensity-label {
  min-width: 60px;
  font-weight: bold;
}

.intensity-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  transition: all 0.3s ease;
  min-width: 100px;
}

.intensity-value {
  min-width: 40px;
  font-weight: bold;
  color: var(--color-text-primary);
}
</style>
