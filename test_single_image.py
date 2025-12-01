#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单张图片的VLM分析
"""

import os
import json
from utils.frame_analyzer import FrameAnalyzer

def test_single_image():
    """测试单张图片分析"""
    # 使用第一张帧图片
    image_path = "test_frames/test_frame_00_00_00_000.jpg"
    
    if not os.path.exists(image_path):
        print(f"错误: 图片文件 '{image_path}' 不存在")
        return
    
    print(f"测试图片: {image_path}")
    
    # 创建分析器
    analyzer = FrameAnalyzer()
    
    print(f"LM Studio端点: {analyzer.endpoint}")
    print(f"VLM模型: {analyzer.model_name}")
    
    # 分析单张图片
    try:
        result = analyzer.analyze_image(image_path)
        
        if result:
            print("分析成功!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("分析失败")
            
    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_image()