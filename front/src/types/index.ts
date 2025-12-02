// 视频信息类型
export interface Video {
  id: string
  filename: string
  size_mb: number
  has_analysis: boolean
  video_path: string
  nsfw_percentage?: number
  average_nsfw_score?: number
  total_frames?: number
  highest_score?: number
  analysis_time?: string
  top_tags?: string[]
}

// 帧分析数据类型
export interface FrameData {
  filename: string
  timestamp: string
  frame_number: number
  nsfw_score: number
  is_nsfw: boolean
  tags: string[]
  description: string
}

// 分析摘要类型
export interface AnalysisSummary {
  total_frames: number
  nsfw_frames: number
  nsfw_percentage: number
  average_nsfw_score: number
  tag_distribution: Record<string, number>
  highest_score_frame: {
    filename: string
    score: number
    tags: string[]
    description: string
  }
  analysis_time: string
}

// 视频信息类型
export interface VideoInfo {
  filename: string
  analysis_time: string
  interval_seconds: number
  total_frames_extracted: number
  frames_analyzed: number
}

// 完整分析数据类型
export interface AnalysisData {
  video_info: VideoInfo
  analysis_summary: AnalysisSummary
  frames: Record<string, FrameData>
  chart_data?: FrameData[]
}

// 图表数据点类型
export interface ChartDataPoint {
  x: number
  y: number
  timestamp: string
  frame_number: number
  tags: string[]
  is_nsfw: boolean
}

// API响应类型
export interface ApiResponse<T> {
  data?: T
  error?: string
}

// 视频库响应类型
export interface VideoListResponse {
  videos: Video[]
}

// 分析响应类型
export interface AnalysisResponse extends AnalysisData {
}