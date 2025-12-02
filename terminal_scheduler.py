#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终端视频调度器 - 纯终端TUI界面
提供文本用户界面让用户选择视频并配置分析参数
"""

import os
import json
import sys
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from utils.video_frame_extractor import extract_frames
from utils.frame_analyzer import FrameAnalyzer
from api_server import APIServer


class TerminalScheduler:
    """终端视频调度器主类"""
    
    def __init__(self):
        self.video_dir = "video"
        self.output_dir = "analysis_results"
        self.frontend_dir = "front/ready2masturbate"
        self.current_analysis = None
        self.api_server = None
        self.api_port = 8000
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化分析器
        self.analyzer = FrameAnalyzer()
        
        # 初始化API服务器
        self.api_server = APIServer(self.api_port)
        
    def get_video_list(self) -> List[Dict[str, Any]]:
        """获取视频文件夹中的所有视频文件"""
        videos = []
        if os.path.exists(self.video_dir):
            for i, filename in enumerate(os.listdir(self.video_dir), 1):
                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                    filepath = os.path.join(self.video_dir, filename)
                    file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                    videos.append({
                        'id': i,
                        'filename': filename,
                        'filepath': filepath,
                        'size_mb': round(file_size, 2)
                    })
        return videos
    
    def get_existing_analysis(self, video_filename: str) -> Optional[Dict[str, Any]]:
        """获取已存在的分析结果"""
        analysis_file = os.path.join(self.output_dir, f"{Path(video_filename).stem}_analysis.json")
        if os.path.exists(analysis_file):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取分析文件失败: {e}")
        return None
    
    def analyze_video(self, video_path: str, interval_seconds: float = 60.0, 
                     max_frames: Optional[int] = None) -> Dict[str, Any]:
        """分析视频文件"""
        video_filename = os.path.basename(video_path)
        video_stem = Path(video_filename).stem
        
        # 创建分析输出目录
        analysis_dir = os.path.join(self.output_dir, f"{video_stem}_frames")
        os.makedirs(analysis_dir, exist_ok=True)
        
        # 步骤1: 提取帧
        print(f"🎬 正在从 {video_filename} 提取帧...")
        frame_count = extract_frames(video_path, analysis_dir, interval_seconds, video_stem)
        
        # 获取帧文件列表
        frame_files = [f for f in os.listdir(analysis_dir) if f.lower().endswith('.jpg')]
        frame_files.sort()
        
        if max_frames:
            frame_files = frame_files[:max_frames]
        
        print(f"📊 将分析 {len(frame_files)} 帧")
        
        # 步骤2: 分析帧内容
        results = {}
        for i, filename in enumerate(frame_files, 1):
            frame_path = os.path.join(analysis_dir, filename)
            print(f"⏳ 分析进度: {i}/{len(frame_files)} - {filename}")
            
            analysis = self.analyzer.analyze_image(frame_path)
            if analysis:
                analysis.update({
                    'filename': filename,
                    'timestamp': self.analyzer._parse_timestamp_from_filename(filename),
                    'frame_number': i
                })
                results[filename] = analysis
        
        # 步骤3: 生成汇总
        summary = self.analyzer._generate_summary(results)
        
        # 步骤4: 保存结果
        analysis_data = {
            'video_info': {
                'filename': video_filename,
                'analysis_time': datetime.now().isoformat(),
                'interval_seconds': interval_seconds,
                'total_frames_extracted': frame_count,
                'frames_analyzed': len(results)
            },
            'analysis_summary': summary,
            'frames': results
        }
        
        analysis_file = os.path.join(self.output_dir, f"{video_stem}_analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析完成，结果保存到: {analysis_file}")
        return analysis_data
    
    def start_api_server(self):
        """启动API服务器"""
        try:
            print(f"🚀 正在启动API服务器...")
            self.api_server.start()
            print(f"✅ API服务器已启动: http://localhost:{self.api_port}")
            return True
            
        except Exception as e:
            print(f"❌ 启动API服务器失败: {e}")
            return False


class TerminalTUI:
    """终端TUI界面"""
    
    def __init__(self):
        self.scheduler = TerminalScheduler()
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """打印标题"""
        print("=" * 60)
        print("🎬 视频内容分析系统 - 终端TUI版本")
        print("=" * 60)
        print()
    
    def print_menu(self):
        """打印主菜单"""
        print("📋 请选择操作:")
        print("1. 📁 查看视频列表")
        print("2. 🔍 分析视频")
        print("3. 🌐 启动API服务器")
        print("4. 📊 查看分析结果")
        print("5. ❌ 退出")
        print()
    
    def show_video_list(self):
        """显示视频列表"""
        self.clear_screen()
        self.print_header()
        print("📁 视频文件列表:")
        print("-" * 60)
        
        videos = self.scheduler.get_video_list()
        if not videos:
            print("❌ 未找到视频文件")
            print("请将视频文件放入 'video' 文件夹")
        else:
            print(f"{'ID':<4} {'文件名':<30} {'大小(MB)':<10} {'状态':<10}")
            print("-" * 60)
            for video in videos:
                analysis = self.scheduler.get_existing_analysis(video['filename'])
                status = "✅已分析" if analysis else "❌未分析"
                print(f"{video['id']:<4} {video['filename']:<30} {video['size_mb']:<10.2f} {status:<10}")
        
        print()
        input("按回车键返回主菜单...")
    
    def analyze_video_menu(self):
        """分析视频菜单"""
        self.clear_screen()
        self.print_header()
        print("🔍 视频分析")
        print("-" * 60)
        
        videos = self.scheduler.get_video_list()
        if not videos:
            print("❌ 未找到视频文件")
            print("请将视频文件放入 'video' 文件夹")
            input("按回车键返回主菜单...")
            return
        
        # 显示视频列表
        print("可用的视频文件:")
        for video in videos:
            print(f"  {video['id']}. {video['filename']} ({video['size_mb']:.2f} MB)")
        
        print()
        try:
            video_id = int(input("请选择视频ID (输入数字): "))
            selected_video = next((v for v in videos if v['id'] == video_id), None)
            
            if not selected_video:
                print("❌ 无效的视频ID")
                input("按回车键返回主菜单...")
                return
            
            # 检查是否已有分析结果
            existing_analysis = self.scheduler.get_existing_analysis(selected_video['filename'])
            if existing_analysis:
                print(f"⚠️  视频 {selected_video['filename']} 已有分析结果")
                choice = input("是否重新分析? (y/n): ").lower()
                if choice != 'y':
                    return
            
            # 获取分析参数
            print()
            print("📊 分析参数设置:")
            interval = float(input("抽帧间隔(秒) [默认60]: ") or "60")
            max_frames_input = input("最大分析帧数 [0=全部]: ").strip()
            max_frames = int(max_frames_input) if max_frames_input and max_frames_input != "0" else None
            
            print()
            print(f"🎬 即将分析视频: {selected_video['filename']}")
            print(f"📊 抽帧间隔: {interval}秒")
            print(f"📊 最大帧数: {max_frames if max_frames else '全部'}")
            print()
            
            choice = input("确认开始分析? (y/n): ").lower()
            if choice != 'y':
                return
            
            # 执行分析
            print()
            start_time = time.time()
            result = self.scheduler.analyze_video(selected_video['filepath'], interval, max_frames)
            end_time = time.time()
            
            print()
            print("=" * 60)
            print("📊 分析结果汇总:")
            print("=" * 60)
            print(f"🎬 视频文件: {result['video_info']['filename']}")
            print(f"⏱️  分析耗时: {end_time - start_time:.2f} 秒")
            print(f"📊 总帧数: {result['analysis_summary']['total_frames']}")
            print(f"🔞 NSFW帧数: {result['analysis_summary']['nsfw_frames']}")
            print(f"📈 平均NSFW分数: {result['analysis_summary']['average_nsfw_score']:.2f}")
            
            # 从highest_score_frame获取最高分数
            if 'highest_score_frame' in result['analysis_summary']:
                max_score = result['analysis_summary']['highest_score_frame']['score']
                print(f"📈 最高NSFW分数: {max_score}")
            else:
                print(f"📈 最高NSFW分数: N/A")
            print("=" * 60)
            
        except ValueError:
            print("❌ 输入无效")
        except Exception as e:
            print(f"❌ 分析过程中发生错误: {e}")
        
        input("按回车键返回主菜单...")
    
    def start_api_server_menu(self):
        """启动API服务器菜单"""
        self.clear_screen()
        self.print_header()
        print("🌐 启动API服务器")
        print("-" * 60)
        
        try:
            success = self.scheduler.start_api_server()
            if success:
                print("✅ API服务器启动成功!")
                print(f"🌐 API地址: http://localhost:{self.scheduler.api_port}")
                print("📝 前端可以通过此API获取分析结果")
                print()
                print("按 Ctrl+C 停止服务器")
                
                # 保持服务器运行
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 API服务器已停止")
            else:
                print("❌ API服务器启动失败")
                
        except Exception as e:
            print(f"❌ 启动API服务器时发生错误: {e}")
        
        input("按回车键返回主菜单...")
    
    def show_analysis_results(self):
        """显示分析结果"""
        self.clear_screen()
        self.print_header()
        print("📊 分析结果")
        print("-" * 60)
        
        # 查找所有分析结果文件
        analysis_files = []
        if os.path.exists(self.scheduler.output_dir):
            for filename in os.listdir(self.scheduler.output_dir):
                if filename.endswith('_analysis.json'):
                    analysis_files.append(filename)
        
        if not analysis_files:
            print("❌ 未找到分析结果")
            input("按回车键返回主菜单...")
            return
        
        print("可用的分析结果:")
        for i, filename in enumerate(analysis_files, 1):
            print(f"  {i}. {filename}")
        
        print()
        try:
            choice = int(input("请选择分析结果 (输入数字): ")) - 1
            if 0 <= choice < len(analysis_files):
                filename = analysis_files[choice]
                filepath = os.path.join(self.scheduler.output_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print()
                print("=" * 60)
                print(f"📊 分析结果: {data['video_info']['filename']}")
                print("=" * 60)
                print(f"🕐 分析时间: {data['video_info']['analysis_time']}")
                print(f"📊 抽帧间隔: {data['video_info']['interval_seconds']}秒")
                print(f"🎬 提取帧数: {data['video_info']['total_frames_extracted']}")
                print(f"🔍 分析帧数: {data['video_info']['frames_analyzed']}")
                print()
                print("📈 NSFW统计:")
                print(f"  🔞 NSFW帧数: {data['analysis_summary']['nsfw_frames']}")
                print(f"  📊 平均分数: {data['analysis_summary']['average_nsfw_score']:.2f}")
                
                # 从highest_score_frame获取最高分数
                if 'highest_score_frame' in data['analysis_summary']:
                    max_score = data['analysis_summary']['highest_score_frame']['score']
                    print(f"  📈 最高分数: {max_score}")
                else:
                    print(f"  📈 最高分数: N/A")
                
                # 计算最低分数
                min_score = 100
                for frame_data in data['frames'].values():
                    if 'nsfw_score' in frame_data:
                        min_score = min(min_score, frame_data['nsfw_score'])
                print(f"  📉 最低分数: {min_score}")
                print("=" * 60)
                
            else:
                print("❌ 无效的选择")
                
        except ValueError:
            print("❌ 输入无效")
        except Exception as e:
            print(f"❌ 读取分析结果时发生错误: {e}")
        
        input("按回车键返回主菜单...")
    
    def run(self):
        """运行TUI界面"""
        while True:
            try:
                self.clear_screen()
                self.print_header()
                self.print_menu()
                
                choice = input("请选择操作 (1-5): ").strip()
                
                if choice == '1':
                    self.show_video_list()
                elif choice == '2':
                    self.analyze_video_menu()
                elif choice == '3':
                    self.start_api_server_menu()
                elif choice == '4':
                    self.show_analysis_results()
                elif choice == '5':
                    print("👋 再见!")
                    break
                else:
                    print("❌ 无效选择，请输入1-5")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                input("按回车键继续...")


def main():
    """主函数"""
    terminal_tui = TerminalTUI()
    terminal_tui.run()


if __name__ == "__main__":
    main()