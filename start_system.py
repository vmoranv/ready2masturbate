#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统启动脚本 - 一键启动视频分析调度器
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("检查系统依赖...")
    
    # 检查Python包
    required_packages = [
        'opencv-python',
        'requests',
        'python-dotenv',
        'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'opencv-python':
                import cv2
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'requests':
                import requests
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        print("或者运行:")
        print("pip install -r utils/requirements.txt")
        return False
    
    print("✅ 所有依赖检查通过")
    return True

def check_lm_studio():
    """检查LM Studio是否运行"""
    print("检查LM Studio状态...")
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        if response.status_code == 200:
            print("✅ LM Studio正在运行")
            return True
    except:
        pass
    
    print("⚠️  LM Studio未运行或无法访问")
    print("请确保LM Studio正在运行并加载了VLM模型")
    return False

def setup_directories():
    """创建必要的目录"""
    print("设置目录结构...")
    
    directories = [
        'video',
        'analysis_results'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 目录已创建: {directory}")

def start_scheduler():
    """启动调度器"""
    print("启动视频分析调度器...")
    
    try:
        # 导入并启动调度器
        from terminal_scheduler import TerminalTUI
        
        scheduler = TerminalTUI()
        print("✅ 调度器启动成功")
        print("=" * 50)
        print("🎬 视频内容分析系统已启动")
        print("=" * 50)
        print("使用说明:")
        print("1. 将视频文件放入 'video' 文件夹")
        print("2. 在调度器中选择视频并设置分析参数")
        print("3. 点击'分析选中视频'开始分析")
        print("4. 点击'启动前端界面'打开Web界面")
        print("=" * 50)
        
        scheduler.run()
        
    except Exception as e:
        print(f"❌ 启动调度器失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 视频内容分析系统启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    # 检查LM Studio
    lm_studio_running = check_lm_studio()
    
    # 设置目录
    setup_directories()
    
    # 检查环境文件
    if not os.path.exists('.env'):
        print("⚠️  未找到.env文件，使用默认配置")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ 已从.env.example复制配置文件")
    
    print("\n" + "=" * 50)
    
    if not lm_studio_running:
        print("⚠️  警告: LM Studio未运行")
        print("分析功能将无法正常工作")
        print("请先启动LM Studio并加载VLM模型")
        
        response = input("\n是否继续启动调度器? (y/n): ").lower()
        if response != 'y':
            print("启动已取消")
            return
    
    # 启动调度器
    try:
        start_scheduler()
    except KeyboardInterrupt:
        print("\n\n👋 系统已退出")
    except Exception as e:
        print(f"\n❌ 系统启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()