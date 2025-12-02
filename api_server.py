#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务器 - 为前端提供视频分析数据接口
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver
import threading
from pathlib import Path


class APIHandler(BaseHTTPRequestHandler):
    """API请求处理器"""
    
    def __init__(self, *args, **kwargs):
        self.output_dir = "analysis_results"
        self.video_dir = "video"
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # 对于非静态文件请求，设置JSON头
        if path not in ['/api/video-file', '/api/thumbnail']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        
        try:
            if path == '/api/videos':
                response = self.get_videos()
                self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            elif path == '/api/analysis':
                video_id = query_params.get('video', [None])[0]
                response = self.get_analysis(video_id)
                self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            elif path == '/api/video-list':
                response = self.get_video_list()
                self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            elif path == '/api/video-file':
                video_path = query_params.get('path', [None])[0]
                if video_path:
                    # Debug print
                    print(f"Serving video: {video_path}")
                    self.serve_file(video_path, 'video/mp4')
                return
            elif path == '/api/thumbnail':
                video_id = query_params.get('id', [None])[0]
                frame_filename = query_params.get('frame', [None])[0]
                self.serve_thumbnail(video_id, frame_filename)
                return
            else:
                response = {'error': 'API endpoint not found'}
                self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            # 如果是BrokenPipeError (客户端断开连接)，忽略
            if not isinstance(e, BrokenPipeError):
                print(f"Error handling request: {e}")
                # 尝试发送错误响应，如果头部还没发送
                try:
                    error_response = {'error': str(e)}
                    self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                except:
                    pass
    
    def get_videos(self) -> dict:
        """获取所有视频及其分析状态"""
        videos = []
        
        if os.path.exists(self.video_dir):
            for filename in os.listdir(self.video_dir):
                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                    video_path = os.path.join(self.video_dir, filename)
                    video_stem = Path(filename).stem
                    
                    # 获取视频信息
                    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                    
                    # 检查分析状态
                    analysis_file = os.path.join(self.output_dir, f"{video_stem}_analysis.json")
                    has_analysis = os.path.exists(analysis_file)
                    
                    video_info = {
                        'id': video_stem,
                        'filename': filename,
                        'size_mb': round(file_size, 2),
                        'has_analysis': has_analysis,
                        'video_path': video_path
                    }
                    
                    # 如果有分析结果，添加摘要信息
                    if has_analysis:
                        try:
                            with open(analysis_file, 'r', encoding='utf-8') as f:
                                analysis_data = json.load(f)
                            
                            summary = analysis_data.get('analysis_summary', {})
                            
                            # 收集所有标签并计算频率
                            all_tags = []
                            frames = analysis_data.get('frames', {})
                            for frame_data in frames.values():
                                tags = frame_data.get('tags', [])
                                all_tags.extend(tags)
                            
                            # 统计标签频率并获取前3个最常见标签
                            tag_counts = {}
                            for tag in all_tags:
                                tag_counts[tag] = tag_counts.get(tag, 0) + 1
                            
                            # 按频率排序并取前3个
                            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                            top_tags_list = [tag for tag, count in top_tags]
                            
                            video_info.update({
                                'nsfw_percentage': summary.get('nsfw_percentage', 0),
                                'average_nsfw_score': summary.get('average_nsfw_score', 0),
                                'total_frames': summary.get('total_frames', 0),
                                'highest_score': summary.get('highest_score_frame', {}).get('score', 0),
                                'analysis_time': analysis_data.get('video_info', {}).get('analysis_time', ''),
                                'top_tags': top_tags_list
                            })
                        except Exception as e:
                            print(f"读取分析文件失败 {filename}: {e}")
                    
                    videos.append(video_info)
        
        return {'videos': videos}
    
    def get_analysis(self, video_id: str) -> dict:
        """获取指定视频的详细分析结果"""
        if not video_id:
            return {'error': 'video parameter is required'}
        
        analysis_file = os.path.join(self.output_dir, f"{video_id}_analysis.json")
        
        if not os.path.exists(analysis_file):
            return {'error': 'Analysis not found for this video'}
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # 处理帧数据，为前端图表准备数据
            frames = analysis_data.get('frames', {})
            chart_data = []
            
            for frame_id, frame_data in frames.items():
                chart_data.append({
                    'timestamp': frame_data.get('timestamp', ''),
                    'frame_number': frame_data.get('frame_number', 0),
                    'nsfw_score': frame_data.get('nsfw_score', 0),
                    'is_nsfw': frame_data.get('is_nsfw', False),
                    'tags': frame_data.get('tags', []),
                    'filename': frame_data.get('filename', ''),
                    'description': frame_data.get('description', '')
                })
            
            # 按帧号排序
            chart_data.sort(key=lambda x: x['frame_number'])
            
            # 添加图表数据到响应
            analysis_data['chart_data'] = chart_data
            
            return analysis_data
            
        except Exception as e:
            return {'error': f'Failed to read analysis: {str(e)}'}
    
    def get_video_list(self) -> dict:
        """获取简单的视频列表（用于下拉选择）"""
        videos = []
        
        if os.path.exists(self.video_dir):
            for filename in os.listdir(self.video_dir):
                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                    video_stem = Path(filename).stem
                    videos.append({
                        'id': video_stem,
                        'name': filename
                    })
        
        return {'videos': videos}

    def serve_file(self, file_path: str, content_type: str):
        """Serve a file with range support"""
        if not file_path or not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return

        file_size = os.path.getsize(file_path)
        
        # Handle Range header
        range_header = self.headers.get('Range')
        if range_header:
            try:
                start, end = range_header.replace('bytes=', '').split('-')
                start = int(start)
                end = int(end) if end else file_size - 1
                length = end - start + 1
                
                self.send_response(206)
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                self.send_header('Content-Length', str(length))
            except ValueError:
                self.send_error(400, "Invalid Range Header")
                return
        else:
            start = 0
            end = file_size - 1
            length = file_size
            self.send_response(200)
            self.send_header('Content-Length', str(length))

        self.send_header('Content-Type', content_type)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = length
                chunk_size = 8192
                while remaining > 0:
                    chunk = f.read(min(chunk_size, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except BrokenPipeError:
            pass
        except Exception as e:
            print(f"Error serving file: {e}")

    def serve_thumbnail(self, video_id: str, frame_filename: str = None):
        """Serve thumbnail for a video"""
        if not video_id:
            self.send_error(400, "Video ID required")
            return
            
        # Try to find a frame image from the analysis results
        frames_dir = os.path.join(self.output_dir, f"{video_id}_frames")
        
        # If a specific frame is requested, try to serve it
        if frame_filename:
            frame_path = os.path.join(frames_dir, frame_filename)
            if os.path.exists(frame_path):
                self.serve_file(frame_path, 'image/jpeg')
                return
        
        # First, check if there's a specific thumbnail file
        thumb_path = os.path.join(self.output_dir, f"{video_id}_thumb.jpg")
        if os.path.exists(thumb_path):
            self.serve_file(thumb_path, 'image/jpeg')
            return
            
        # If frames directory exists, serve the first frame as thumbnail
        if os.path.exists(frames_dir):
            try:
                # Get all frame files and sort them
                frame_files = [f for f in os.listdir(frames_dir) if f.endswith('.jpg')]
                if frame_files:
                    frame_files.sort()
                    # Use the first frame as thumbnail
                    first_frame_path = os.path.join(frames_dir, frame_files[0])
                    if os.path.exists(first_frame_path):
                        self.serve_file(first_frame_path, 'image/jpeg')
                        return
            except Exception as e:
                print(f"Error reading frame directory: {e}")
        
        # Fallback: try to find any frame image for this video
        self.send_error(404, "Thumbnail not found")
    
    def log_message(self, format, *args):
        """重写日志方法以减少输出"""
        pass


class APIServer:
    """API服务器类"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self):
        """启动API服务器"""
        def run_server():
            with socketserver.TCPServer(("", self.port), APIHandler) as httpd:
                print(f"API服务器运行在 http://localhost:{self.port}")
                httpd.serve_forever()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        import time
        time.sleep(1)
        
        return f"http://localhost:{self.port}"


def main():
    """主函数 - 用于测试"""
    server = APIServer(8000)
    server.start()
    
    print("API服务器已启动，按 Ctrl+C 停止")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n服务器已停止")


if __name__ == "__main__":
    main()