# 视频抽帧工具函数

这是一个用于从视频中按照指定时间间隔提取帧的Python工具函数库，提取的帧会以时间戳命名保存。

## 功能特性

- 按照指定时间间隔从视频中提取帧
- 自动将帧以时间戳格式命名（HH_MM_SS_mmm）
- 支持自定义输出文件名前缀
- 支持多种视频格式（MP4、AVI、MOV等）
- 纯函数库，无命令行界面和输出信息

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install opencv-python numpy
```

## 使用方法

### 导入函数

```python
from utils.video_frame_extractor import extract_frames
```

### 函数签名

```python
def extract_frames(video_path, output_dir, interval_seconds, prefix="frame"):
    """
    从视频中提取帧
    
    Args:
        video_path (str): 视频文件路径
        output_dir (str): 输出目录
        interval_seconds (float): 抽帧间隔（秒）
        prefix (str): 输出文件名前缀，默认为"frame"
        
    Returns:
        int: 提取的帧数
    """
```

### 使用示例

```python
# 基本用法：每5秒提取一帧
from utils.video_frame_extractor import extract_frames

extracted_count = extract_frames(
    video_path="input.mp4",
    output_dir="output_frames",
    interval_seconds=5
)

# 自定义前缀：每2.5秒提取一帧
extracted_count = extract_frames(
    video_path="video.avi",
    output_dir="frames",
    interval_seconds=2.5,
    prefix="my_frame"
)

# 每10秒提取一帧
extracted_count = extract_frames(
    video_path="movie.mp4",
    output_dir="./frames",
    interval_seconds=10,
    prefix="scene"
)
```

## 输出文件命名

提取的帧会按照以下格式命名：
```
{前缀}_{时}_{分}_{秒}_{毫秒}.jpg
```

例如：
- `frame_00_00_05_000.jpg` - 第5秒的帧
- `scene_00_01_30_500.jpg` - 第1分30.5秒的帧
- `my_frame_00_00_10_000.jpg` - 第10秒的帧

## 返回值

函数返回提取的帧数（整数），如果提取失败则返回0。

## 注意事项

1. 确保输入视频文件存在且可读
2. 输出目录会自动创建（如果不存在）
3. 抽帧间隔必须大于0秒
4. 支持的视频格式取决于OpenCV的编译配置
5. 提取的帧保存为JPG格式
6. 函数不会产生任何输出信息，只返回提取的帧数

## 系统要求

- Python 3.6+
- OpenCV 4.5.0+
- NumPy 1.19.0+