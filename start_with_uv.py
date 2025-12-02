#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用uv管理的系统启动脚本
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def check_uv_installed():
    """检查uv是否安装"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ uv未安装")
    print("请安装uv: https://docs.astral.sh/uv/getting-started/installation/")
    return False

def setup_virtual_environment():
    """设置虚拟环境"""
    print("设置uv虚拟环境...")
    
    # 创建虚拟环境
    try:
        subprocess.run(['uv', 'venv'], check=True)
        print("✅ 虚拟环境创建成功")
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e):
            print("✅ 虚拟环境已存在")
        else:
            print(f"❌ 创建虚拟环境失败: {e}")
            return False
    
    # 安装依赖
    try:
        print("安装项目依赖...")
        subprocess.run(['uv', 'pip', 'install', '-e', '.'], check=True)
        print("✅ 依赖安装成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    
    return True

def check_lm_studio():
    """检查LM Studio是否运行"""
    print("检查LM Studio状态...")
    
    try:
        # 使用uv运行检测脚本
        result = subprocess.run([
            'uv', 'run', 'python', '-c',
            '''
import requests
try:
    response = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
    if response.status_code == 200:
        models = response.json().get("data", [])
        vl_models = [m for m in models if "vl" in m.get("id", "").lower() or "vision" in m.get("id", "").lower()]
        if vl_models:
            print(f"✅ LM Studio正在运行，检测到VLM模型: {vl_models[0]["id"]}")
            exit(0)
        else:
            print("⚠️  LM Studio运行中，但未检测到VLM模型")
            exit(1)
    else:
        print(f"⚠️  LM Studio响应异常，状态码: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"⚠️  LM Studio未运行或无法访问: {e}")
    exit(1)
            '''
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(result.stdout.strip())
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  LM Studio检测超时")
        return False
    except Exception as e:
        print(f"⚠️  LM Studio检测失败: {e}")
        return False

def setup_directories():
    """创建必要的目录"""
    print("设置目录结构...")
    
    directories = [
        'video',
        'analysis_results',
        'test_frames'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 目录已创建: {directory}")

def start_scheduler():
    """启动调度器"""
    print("启动终端TUI调度器...")
    
    try:
        # 使用uv运行终端调度器
        subprocess.run(['uv', 'run', 'python', 'terminal_scheduler.py'])
        
    except Exception as e:
        print(f"❌ 启动调度器失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 视频内容分析系统启动器 (uv版本)")
    print("=" * 50)
    
    # 检查uv
    if not check_uv_installed():
        input("按回车键退出...")
        return
    
    # 设置虚拟环境
    if not setup_virtual_environment():
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
        print("=" * 50)
        print("🎬 视频内容分析系统已启动")
        print("=" * 50)
        print("使用说明:")
        print("1. 将视频文件放入 'video' 文件夹")
        print("2. 在调度器中选择视频并设置分析参数")
        print("3. 点击'分析选中视频'开始分析")
        print("4. 点击'启动前端界面'打开Web界面")
        print("=" * 50)
        
        start_scheduler()
        
    except KeyboardInterrupt:
        print("\n\n👋 系统已退出")
    except Exception as e:
        print(f"\n❌ 系统启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()