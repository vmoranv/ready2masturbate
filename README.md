# 🎬 视频内容分析系统

基于VLM模型的智能视频内容分析系统，支持自动抽帧、NSFW内容分析和可视化展示。

## ✨ 功能特性

- 🎥 **视频抽帧**: 按指定时间间隔从视频中提取帧
- 🧠 **AI分析**: 使用LM Studio的VLM模型进行NSFW内容分析
- 🏷️ **智能标签**: 自动生成描述性标签，支持自定义标签
- 📊 **可视化展示**: 实时曲线图表显示NSFW分数变化
- 🎬 **视频播放器**: 集成播放器，支持时间轴同步
- 📚 **视频库管理**: 影视库风格的视频管理界面
- 🖥️ **双界面**: TUI调度器 + Web前端

## 🚀 快速开始

### 1. 环境准备

#### 系统要求
- Python 3.8+
- uv (推荐的Python包管理器)
- LM Studio (用于VLM模型)
- 现代浏览器 (Chrome/Firefox/Edge)

#### 安装uv (推荐)
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 安装依赖

**方式1: 使用uv (推荐)**
```bash
# 一键设置虚拟环境和依赖
python start_with_uv.py

# 或者手动设置
uv venv                    # 创建虚拟环境
uv pip install -e .       # 安装项目依赖
```

**方式2: 使用pip**
```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者手动安装
pip install opencv-python requests python-dotenv

# 安装前端依赖
cd front/ready2masturbate
npm install
cd ../..
```

### 2. LM Studio配置

1. 下载并启动 [LM Studio](https://lmstudio.ai/)
2. 在LM Studio中搜索并加载VLM模型:
   - 推荐模型: `mradermacher/Qwen3-VL-8B-NSFW-Caption-V4.5-GGUF`
   - 或其他支持视觉的模型
3. 确保LM Studio在 `http://127.0.0.1:1234` 运行

### 3. 启动系统

#### 方法一: 使用uv启动脚本 (推荐)
```bash
python start_with_uv.py
```

#### 方法二: 使用传统启动脚本
```bash
python start_system.py
```

#### 方法三: 手动启动
```bash
# 使用uv
uv run python video_scheduler.py

# 或者使用传统方式
python video_scheduler.py
```

### 4. 使用流程

1. **添加视频**: 将视频文件放入 `video/` 文件夹
2. **分析视频**: 在TUI调度器中选择视频并设置分析参数
3. **查看结果**: 启动Web前端界面查看分析结果

## 🎛️ 调度器功能

### TUI界面功能
- 📋 视频列表管理
- ⚙️ 分析参数配置 (抽帧间隔、最大帧数)
- 🔄 批量视频分析
- 🌐 启动Web前端服务

### 分析参数
- **抽帧间隔**: 1-300秒 (默认60秒)
- **最大帧数**: 限制分析帧数 (0=全部)
- **VLM模型**: 支持LM Studio中的任何视觉模型

## 🌐 Web前端功能

### 视频库界面
- 📊 统计信息展示
- 🎬 卡片式视频列表
- 🏷️ NSFW等级标识
- ⏱️ 分析时间显示

### 视频播放器
- ▶️ 视频播放控制
- 📈 实时NSFW分数曲线
- 🏷️ 标签统计图表
- 📍 点击图表查看帧详情
- 🔄 播放进度与分析数据同步

### 数据可视化
- 📈 Chart.js曲线图表
- 🎨 颜色编码NSFW等级
- 📊 标签分布统计
- 🔍 交互式数据探索

## 🔧 配置说明

### 环境变量 (.env)
```env
# LM Studio配置
LM_STUDIO_ENDPOINT=http://127.0.0.1:1234
VLM_MODEL_NAME=qwen3-vl-8b-nsfw-caption-v4.5
```

### VLM提示词配置 (utils/prompts.json)
```json
{
  "nsfw_analysis": {
    "role": "You are an expert NSFW Content Analyzer...",
    "example_categories": [
      "exposed_breasts (Visible nipples or full breast exposure)",
      "exposed_genitalia (Penis, vagina, testicles)",
      // ... 更多示例
    ],
    "scoring_rules": {
      "0-10": "Safe / Family friendly.",
      "11-40": "Suggestive / Mild",
      "41-70": "NSFW / Borderline", 
      "71-100": "Explicit / Hardcore"
    }
  }
}
```

## 📊 API接口

### 获取视频列表
```http
GET http://localhost:8000/api/videos
```

### 获取分析结果
```http
GET http://localhost:8000/api/analysis?video=<video_id>
```

### 视频文件服务
```http
GET http://localhost:5173/api/video-file?path=<video_path>
```

## 🎯 使用场景

- 📺 **视频内容审核**: 自动检测敏感内容
- 📊 **内容分析统计**: 批量分析视频内容分布
- 🔍 **时间点定位**: 快速定位特定内容时间点
- 📈 **趋势分析**: 分析内容强度变化趋势
- 🏷️ **自动标签**: 生成内容描述标签

## ⚠️ 注意事项

1. **LM Studio要求**: 必须先启动LM Studio并加载VLM模型
2. **硬件要求**: VLM分析需要较好的GPU支持
3. **分析时间**: 大视频文件分析可能需要较长时间
4. **存储空间**: 抽帧和分析结果会占用额外存储空间
5. **网络要求**: 前端需要访问API服务器

## 🔧 故障排除

### 常见问题

**Q: LM Studio连接失败**
A: 检查LM Studio是否在1234端口运行，模型是否已加载

**Q: 前端无法加载数据**
A: 检查API服务器是否在8000端口运行

**Q: 视频播放失败**
A: 检查视频文件路径和格式是否支持

**Q: 分析结果不准确**
A: 尝试调整提示词配置或更换VLM模型

### 日志查看
- 调度器日志: TUI界面状态栏
- API服务器日志: 控制台输出
- 前端日志: 浏览器开发者工具

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
