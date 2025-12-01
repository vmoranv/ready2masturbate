#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
限制数量的完整工作流程测试
"""

import os
import json
from utils.video_frame_extractor import extract_frames
from utils.frame_analyzer import FrameAnalyzer

def test_limited_workflow():
    """测试限制数量的完整工作流程"""
    print("=== 限制数量完整工作流程测试 ===")
    
    # 配置参数
    video_path = "video/1.mp4"
    frames_dir = "test_frames_limited"
    analysis_output = os.path.join(frames_dir, "analysis.json")
    interval_seconds = 60.0  # 60秒抽一帧
    prefix = "test_frame"
    max_frames = 5  # 最多处理5帧
    
    # 步骤1: 从视频中提取帧
    print(f"步骤1: 从视频中提取帧...")
    print(f"视频文件: {video_path}")
    print(f"帧输出目录: {frames_dir}")
    print(f"抽帧间隔: {interval_seconds}秒")
    print(f"文件前缀: {prefix}")
    
    try:
        frame_count = extract_frames(video_path, frames_dir, interval_seconds, prefix)
        print(f"成功提取 {frame_count} 帧")
        
        # 获取实际的帧文件列表
        frame_files = [f for f in os.listdir(frames_dir) if f.lower().endswith('.jpg')]
        frame_files.sort()
        
        # 限制处理的帧数量
        frame_files = frame_files[:max_frames]
        print(f"限制处理前 {len(frame_files)} 帧")
        
        # 步骤2: 使用LM Studio VLM模型分析帧内容
        print(f"\n步骤2: 使用LM Studio VLM模型分析帧内容...")
        
        analyzer = FrameAnalyzer()
        print(f"LM Studio端点: {analyzer.endpoint}")
        print(f"VLM模型: {analyzer.model_name}")
        
        results = {}
        
        for i, filename in enumerate(frame_files, 1):
            image_path = os.path.join(frames_dir, filename)
            print(f"分析进度: {i}/{len(frame_files)} - {filename}")
            
            # 分析图片
            analysis = analyzer.analyze_image(image_path)
            
            if analysis:
                # 添加额外信息
                analysis["filename"] = filename
                analysis["timestamp"] = analyzer._parse_timestamp_from_filename(filename)
                analysis["frame_number"] = i
                
                results[filename] = analysis
                print(f"  NSFW分数: {analysis.get('nsfw_score', 0)}, 标签: {analysis.get('tags', [])}")
            else:
                print(f"  分析失败: {filename}")
        
        # 生成汇总报告
        summary = analyzer._generate_summary(results)
        
        # 保存结果
        analyzer._save_results(results, summary, analysis_output)
        
        print(f"\n=== 分析完成 ===")
        print(f"总帧数: {summary['total_frames']}")
        print(f"NSFW帧数: {summary['nsfw_frames']}")
        print(f"NSFW比例: {summary['nsfw_percentage']:.1f}%")
        print(f"平均NSFW分数: {summary['average_nsfw_score']}")
        print(f"最高分帧: {summary['highest_score_frame']['filename']} (分数: {summary['highest_score_frame']['score']})")
        print(f"分析结果已保存到: {analysis_output}")
        
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_limited_workflow()