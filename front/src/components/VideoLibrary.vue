<script setup lang="ts">
import { computed } from 'vue'
import type { Video } from '../types'

interface Props {
  videos: Video[]
}

interface Emits {
  (e: 'select-video', video: Video): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 计算属性
const analyzedVideos = computed(() => 
  props.videos.filter(video => video.has_analysis)
)

const unanalyzedVideos = computed(() => 
  props.videos.filter(video => !video.has_analysis)
)

// 格式化文件大小
const formatFileSize = (sizeMb: number) => {
  if (sizeMb < 1024) {
    return `${sizeMb.toFixed(1)} MB`
  }
  return `${(sizeMb / 1024).toFixed(1)} GB`
}

// 格式化时间
const formatTime = (timeString: string) => {
  if (!timeString) return 'Unknown'
  try {
    const date = new Date(timeString)
    // Return relative time or simple date
    return date.toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

// 选择视频
const selectVideo = (video: Video) => {
  emit('select-video', video)
}
</script>

<template>
  <div class="video-library">
    <!-- Main Video Grid -->
    <section v-if="analyzedVideos.length > 0" class="video-section">
      <div class="section-header">
        <h2>Recommended Videos</h2>
      </div>
      <div class="video-grid">
        <div 
          v-for="video in analyzedVideos" 
          :key="video.id"
          class="video-card"
          @click="selectVideo(video)"
        >
          <div class="thumbnail-container">
            <img 
              v-if="video.has_analysis"
              :src="`http://localhost:8000/api/thumbnail?id=${video.id}`" 
              class="video-thumbnail-img"
              @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
            />
            <div class="thumbnail-placeholder" :class="{ 'has-thumb': video.has_analysis }">
              <span class="play-icon">▶</span>
            </div>
            <span class="duration-badge">{{ video.total_frames || '0' }} f</span>
            <div class="hd-badge">HD</div>
          </div>
          
          <div class="video-details">
            <h3 class="video-title" :title="video.filename">
              {{ video.filename }}
            </h3>
            
            <div class="video-meta">
              <span class="upload-date">{{ formatTime(video.analysis_time || '') }}</span>
            </div>

            <div class="video-tags" v-if="video.top_tags && video.top_tags.length > 0">
              <span v-for="tag in video.top_tags.slice(0, 3)" :key="tag" class="video-tag">
                {{ tag }}
              </span>
            </div>
            
            <div class="uploader">
              <span v-if="video.average_nsfw_score" class="rating-badge">
                NSFW: {{ (video.average_nsfw_score).toFixed(2) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Unanalyzed / New Videos -->
    <section v-if="unanalyzedVideos.length > 0" class="video-section">
      <div class="section-header">
        <h2>New Arrivals (Pending Analysis)</h2>
      </div>
      <div class="video-grid">
        <div 
          v-for="video in unanalyzedVideos" 
          :key="video.id"
          class="video-card unanalyzed"
          @click="selectVideo(video)"
        >
          <div class="thumbnail-container">
            <div class="thumbnail-placeholder">
              <span class="pending-icon">⏳</span>
            </div>
            <span class="duration-badge">PENDING</span>
          </div>
          
          <div class="video-details">
            <h3 class="video-title" :title="video.filename">
              {{ video.filename }}
            </h3>
            
            <div class="video-meta">
              <span class="file-size">{{ formatFileSize(video.size_mb) }}</span>
            </div>
            
            <div class="action-text">Click to Analyze</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Empty State -->
    <div v-if="videos.length === 0" class="empty-state">
      <div class="empty-icon">📂</div>
      <h3>No videos found</h3>
      <p>Add videos to the video folder to get started.</p>
    </div>
  </div>
</template>

<style scoped>
.video-library {
  width: 100%;
}

.section-header {
  margin-bottom: 20px;
  border-bottom: 1px solid #333;
  padding-bottom: 10px;
}

.section-header h2 {
  font-size: 20px;
  color: var(--color-text-primary);
  font-weight: bold;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* Default 4 columns */
  gap: 20px;
  margin-bottom: 40px;
}

@media (min-width: 1600px) {
  .video-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 1200px) {
  .video-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.video-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.video-card:hover .video-title {
  color: var(--color-accent);
}

.thumbnail-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
  background: #222;
  overflow: hidden;
  margin-bottom: 10px;
}

.thumbnail-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #333;
  color: #555;
  font-size: 40px;
  transition: background 0.3s;
  z-index: 2;
}

.video-card:hover .thumbnail-placeholder {
  background: #444;
  color: var(--color-accent);
}

.duration-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2px 5px;
  font-size: 12px;
  border-radius: 2px;
  font-weight: bold;
  z-index: 4;
}

.hd-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  background: var(--color-accent);
  color: black;
  padding: 1px 4px;
  font-size: 10px;
  border-radius: 2px;
  font-weight: bold;
  opacity: 0.9;
  z-index: 4;
}

.video-details {
  padding: 0 5px;
}

.video-title {
  font-size: 14px;
  color: var(--color-text-primary);
  margin-bottom: 5px;
  line-height: 1.4;
  height: 2.8em; /* 2 lines */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-weight: bold;
}

.video-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 5px;
}

.uploader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.uploader-name:hover {
  color: var(--color-text-primary);
}

.rating-badge {
  background: rgba(255, 163, 26, 0.2);
  color: #ffa31a;
  padding: 1px 4px;
  border-radius: 2px;
  font-size: 11px;
  font-weight: bold;
}

.video-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 5px;
}

.video-tag {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-secondary);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  white-space: nowrap;
}

/* Unanalyzed specific styles */
.video-card.unanalyzed .thumbnail-placeholder {
  background: #2a2a2a;
}

.action-text {
  color: var(--color-accent);
  font-size: 12px;
  margin-top: 5px;
}

.empty-state {
  text-align: center;
  padding: 100px 0;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.video-thumbnail-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

.thumbnail-placeholder.has-thumb {
  background: transparent;
  opacity: 0;
  z-index: 3;
}

.video-card:hover .thumbnail-placeholder.has-thumb {
  opacity: 1;
  background: rgba(0,0,0,0.3);
}
</style>