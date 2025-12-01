#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频抽帧工具函数
从指定视频中按照时间间隔提取帧，并保存为带时间戳的图片文件
"""

import cv2
import os
from datetime import timedelta


def format_timestamp(seconds):
    """
    将秒数格式化为时间戳字符串 (HH_MM_SS_mmm)
    
    Args:
        seconds (float): 秒数
        
    Returns:
        str: 格式化的时间戳字符串
    """
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    
    return f"{hours:02d}_{minutes:02d}_{seconds:02d}_{milliseconds:03d}"


def extract_frames(video_path, output_dir, interval_seconds, prefix="frame"):
    """
    从视频中提取帧
    
    Args:
        video_path (str): 视频文件路径
        output_dir (str): 输出目录
        interval_seconds (float): 抽帧间隔（秒）
        prefix (str): 输出文件名前缀
        
    Returns:
        int: 提取的帧数
    """
    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        return 0
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    
    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 计算抽帧间隔的帧数
    interval_frames = int(fps * interval_seconds)
    if interval_frames < 1:
        interval_frames = 1
    
    extracted_count = 0
    current_frame = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 计算当前帧的时间戳
        current_time = current_frame / fps
        
        # 按照间隔提取帧
        if current_frame % interval_frames == 0:
            # 格式化时间戳
            timestamp_str = format_timestamp(current_time)
            filename = f"{prefix}_{timestamp_str}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            # 保存帧
            cv2.imwrite(output_path, frame)
            extracted_count += 1
        
        current_frame += 1
    
    # 释放资源
    cap.release()
    
    return extracted_count
