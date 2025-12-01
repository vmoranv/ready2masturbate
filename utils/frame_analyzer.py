#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帧内容分析工具
使用LM Studio的VLM模型对已抽帧的图片进行NSFW内容分析并生成JSON标签
"""

import json
import os
import base64
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class FrameAnalyzer:
    """帧内容分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.endpoint = os.getenv("LM_STUDIO_ENDPOINT")
        self.model_name = os.getenv("VLM_MODEL_NAME")
        self.prompt_data = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        """加载提示词配置"""
        with open("utils/prompts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    
    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _call_vlm_api(self, base64_image: str, prompt: str) -> Optional[Dict[str, Any]]:
        """调用VLM API"""
        # 构建请求数据
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        # 发送请求
        response = requests.post(
            f"{self.endpoint}/v1/chat/completions",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 解析JSON结果
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    print(f"无法解析JSON响应: {content}")
                    return None
        else:
            print(f"API请求失败: {response.status_code} - {response.text}")
            return None
    
    def analyze_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """分析单张图片"""
        # 编码图片
        base64_image = self._encode_image_to_base64(image_path)
        
        # 构建完整的prompt字符串
        prompt_config = self.prompt_data["nsfw_analysis"]
        examples = '\n'.join([f"  - {cat}" for cat in prompt_config.get('example_categories', [])])
        
        prompt = f"""{prompt_config['role']}

Example categories for reference:
{examples}

Scoring Rules:
{json.dumps(prompt_config['scoring_rules'], indent=2)}

Output Format (respond with valid JSON only):
{json.dumps(prompt_config['output_format'], indent=2)}

Analyze the image and provide the response in the specified JSON format."""
        
        # 调用API
        return self._call_vlm_api(base64_image, prompt)
    
    def analyze_frames_directory(self, frames_dir: str, output_file: str = None) -> Dict[str, Any]:
        """
        分析目录中的所有帧并生成JSON标签
        
        Args:
            frames_dir: 帧图片目录
            output_file: 输出JSON文件路径，默认为frames_dir/analysis.json
            
        Returns:
            分析结果汇总
        """
        if output_file is None:
            output_file = os.path.join(frames_dir, "analysis.json")
        
        # 获取所有JPG文件
        image_files = [f for f in os.listdir(frames_dir) if f.lower().endswith('.jpg')]
        image_files.sort()
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        results = {}
        
        for i, filename in enumerate(image_files, 1):
            image_path = os.path.join(frames_dir, filename)
            print(f"分析进度: {i}/{len(image_files)} - {filename}")
            
            # 解析时间戳
            timestamp = self._parse_timestamp_from_filename(filename)
            
            # 分析图片
            analysis = self.analyze_image(image_path)
            
            if analysis:
                # 添加额外信息
                analysis["filename"] = filename
                analysis["timestamp"] = timestamp
                analysis["frame_number"] = i
                
                results[filename] = analysis
            else:
                print(f"分析失败: {filename}")
        
        # 生成汇总报告
        summary = self._generate_summary(results)
        
        # 保存结果
        self._save_results(results, summary, output_file)
        
        return {
            "summary": summary,
            "frames": results
        }
    
    def _parse_timestamp_from_filename(self, filename: str) -> str:
        """从文件名解析时间戳"""
        # 文件名格式: prefix_HH_MM_SS_mmm.jpg
        parts = filename.replace('.jpg', '').split('_')
        if len(parts) >= 5:
            _, hours, minutes, seconds, milliseconds = parts[-5:]
            return f"{hours}:{minutes}:{seconds}.{milliseconds}"
        return filename
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析汇总"""
        total_frames = len(results)
        nsfw_frames = sum(1 for r in results.values() if r.get("is_nsfw", False))
        
        # 统计标签
        all_tags = []
        for result in results.values():
            all_tags.extend(result.get("tags", []))
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 计算平均分数
        scores = [r.get("nsfw_score", 0) for r in results.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # 找出最高分的帧
        if results:
            max_score_frame = max(results.items(), key=lambda x: x[1].get("nsfw_score", 0))
            highest_score_info = {
                "filename": max_score_frame[0],
                "score": max_score_frame[1].get("nsfw_score", 0),
                "tags": max_score_frame[1].get("tags", []),
                "description": max_score_frame[1].get("description", "")
            }
        else:
            highest_score_info = {
                "filename": "",
                "score": 0,
                "tags": [],
                "description": "No frames analyzed"
            }
        
        return {
            "total_frames": total_frames,
            "nsfw_frames": nsfw_frames,
            "nsfw_percentage": (nsfw_frames / total_frames * 100) if total_frames > 0 else 0,
            "average_nsfw_score": round(avg_score, 2),
            "tag_distribution": tag_counts,
            "highest_score_frame": highest_score_info,
            "analysis_time": datetime.now().isoformat()
        }
    
    def _save_results(self, results: Dict[str, Any], summary: Dict[str, Any], output_file: str):
        """保存分析结果到JSON文件"""
        output_data = {
            "analysis_summary": summary,
            "frames": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"分析结果已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="帧内容分析工具")
    parser.add_argument("frames_dir", help="帧图片目录路径")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.frames_dir):
        print(f"错误: 目录 '{args.frames_dir}' 不存在")
        return
    
    # 创建分析器并执行分析
    analyzer = FrameAnalyzer()
    
    try:
        result = analyzer.analyze_frames_directory(args.frames_dir, args.output)
        print("分析成功完成！")
        
    except KeyboardInterrupt:
        print("\n分析被用户中断")
    except Exception as e:
        print(f"分析过程中发生错误: {e}")


if __name__ == "__main__":
    main()