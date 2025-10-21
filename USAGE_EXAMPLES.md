# 视频处理预制件使用示例

本文档提供了所有视频处理功能的使用示例。

## 功能列表

1. [视频转音频](#1-视频转音频-video_to_audio)
2. [视频拼接](#2-视频拼接-concatenate_videos)
3. [视频剪辑](#3-视频剪辑-trim_video)
4. [调整视频尺寸](#4-调整视频尺寸-resize_video)
5. [提取音频片段](#5-提取音频片段-extract_audio_segment)
6. [获取视频信息](#6-获取视频信息-get_video_info)

---

## 1. 视频转音频 (video_to_audio)

将视频文件转换为音频文件。

### 基本用法

```python
from src.main import video_to_audio

# 默认转换为 mp3 格式
result = video_to_audio("input.mp4")
print(result)
# {
#     "success": True,
#     "output_file": "input.mp3",
#     "format": "mp3",
#     "duration": 120.5
# }
```

### 指定输出格式和路径

```python
# 转换为 wav 格式
result = video_to_audio(
    video_path="input.mp4",
    output_path="output/audio.wav",
    audio_format="wav",
    audio_bitrate="320k"
)
```

### 支持的音频格式

- `mp3` (默认)
- `wav`
- `aac`
- `flac`
- `ogg`

---

## 2. 视频拼接 (concatenate_videos)

将多个视频文件拼接成一个完整的视频。

### 基本用法

```python
from src.main import concatenate_videos

# 拼接多个视频
result = concatenate_videos([
    "video1.mp4",
    "video2.mp4",
    "video3.mp4"
])
print(result)
# {
#     "success": True,
#     "output_file": "concatenated_output.mp4",
#     "total_duration": 360.5,
#     "video_count": 3
# }
```

### 指定输出路径

```python
result = concatenate_videos(
    video_paths=["intro.mp4", "main.mp4", "outro.mp4"],
    output_path="final_video.mp4"
)
```

---

## 3. 视频剪辑 (trim_video)

从视频中提取指定时间段的内容。

### 基本用法

```python
from src.main import trim_video

# 提取 10 秒到 30 秒的内容
result = trim_video(
    video_path="input.mp4",
    start_time=10,
    end_time=30
)
print(result)
# {
#     "success": True,
#     "output_file": "input_trimmed.mp4",
#     "duration": 20.0,
#     "start_time": 10,
#     "end_time": 30
# }
```

### 指定输出路径

```python
result = trim_video(
    video_path="long_video.mp4",
    start_time=60,
    end_time=120,
    output_path="highlight.mp4"
)
```

---

## 4. 调整视频尺寸 (resize_video)

调整视频的分辨率或大小。

### 按宽度调整（保持宽高比）

```python
from src.main import resize_video

# 调整宽度为 1280px，高度自动计算
result = resize_video(
    video_path="input.mp4",
    width=1280
)
```

### 按高度调整（保持宽高比）

```python
# 调整高度为 720px，宽度自动计算
result = resize_video(
    video_path="input.mp4",
    height=720
)
```

### 同时指定宽度和高度

```python
# 强制调整为指定尺寸（可能会改变宽高比）
result = resize_video(
    video_path="input.mp4",
    width=1920,
    height=1080
)
```

### 按缩放比例调整

```python
# 缩小到原来的 50%
result = resize_video(
    video_path="input.mp4",
    scale=0.5
)

# 放大到原来的 150%
result = resize_video(
    video_path="input.mp4",
    scale=1.5
)
```

---

## 5. 提取音频片段 (extract_audio_segment)

从音频文件中提取指定时间段。

### 基本用法

```python
from src.main import extract_audio_segment

# 提取 5 秒到 15 秒的音频
result = extract_audio_segment(
    audio_path="audio.mp3",
    start_time=5,
    end_time=15
)
print(result)
# {
#     "success": True,
#     "output_file": "audio_segment.mp3",
#     "duration": 10.0,
#     "start_time": 5,
#     "end_time": 15
# }
```

### 指定输出路径

```python
result = extract_audio_segment(
    audio_path="podcast.mp3",
    start_time=120,
    end_time=180,
    output_path="highlight_clip.mp3"
)
```

---

## 6. 获取视频信息 (get_video_info)

获取视频文件的详细信息。

### 基本用法

```python
from src.main import get_video_info

result = get_video_info("video.mp4")
print(result)
# {
#     "success": True,
#     "info": {
#         "duration": 120.5,
#         "fps": 30,
#         "size": [1920, 1080],
#         "width": 1920,
#         "height": 1080,
#         "has_audio": True,
#         "file_size_bytes": 52428800,
#         "file_size_mb": 50.0
#     }
# }
```

### 使用返回的信息

```python
result = get_video_info("video.mp4")

if result["success"]:
    info = result["info"]
    print(f"视频时长: {info['duration']} 秒")
    print(f"分辨率: {info['width']}x{info['height']}")
    print(f"帧率: {info['fps']} FPS")
    print(f"文件大小: {info['file_size_mb']} MB")
    print(f"是否有音频: {'是' if info['has_audio'] else '否'}")
```

---

## 错误处理

所有函数都返回统一的错误格式：

```python
{
    "success": False,
    "error": "错误描述信息",
    "error_code": "ERROR_CODE"
}
```

### 常见错误代码

- `FILE_NOT_FOUND`: 文件不存在
- `NO_AUDIO_TRACK`: 视频文件不包含音频轨道
- `INVALID_START_TIME`: 开始时间无效（负数）
- `INVALID_TIME_RANGE`: 时间范围无效（结束时间小于等于开始时间）
- `TIME_OUT_OF_RANGE`: 时间超出文件长度
- `MISSING_SIZE_PARAMETER`: 缺少尺寸参数
- `INSUFFICIENT_VIDEOS`: 拼接时提供的视频数量不足
- `CONVERSION_ERROR`: 转换失败
- `CONCATENATION_ERROR`: 拼接失败
- `TRIM_ERROR`: 剪辑失败
- `RESIZE_ERROR`: 调整大小失败
- `EXTRACT_ERROR`: 提取失败
- `INFO_ERROR`: 获取信息失败

### 错误处理示例

```python
result = video_to_audio("input.mp4")

if result["success"]:
    print(f"成功！输出文件: {result['output_file']}")
else:
    print(f"失败: {result['error']}")
    print(f"错误代码: {result['error_code']}")
```

---

## 批量处理示例

### 批量转换视频为音频

```python
import os
from src.main import video_to_audio

video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]

for video_file in video_files:
    result = video_to_audio(video_file)
    if result["success"]:
        print(f"✅ {video_file} -> {result['output_file']}")
    else:
        print(f"❌ {video_file}: {result['error']}")
```

### 批量剪辑视频

```python
from src.main import trim_video

clips = [
    {"input": "long_video.mp4", "start": 0, "end": 30, "output": "clip1.mp4"},
    {"input": "long_video.mp4", "start": 30, "end": 60, "output": "clip2.mp4"},
    {"input": "long_video.mp4", "start": 60, "end": 90, "output": "clip3.mp4"},
]

for clip in clips:
    result = trim_video(
        video_path=clip["input"],
        start_time=clip["start"],
        end_time=clip["end"],
        output_path=clip["output"]
    )
    if result["success"]:
        print(f"✅ 已创建 {clip['output']}")
```

---

## 与 AI 平台集成

当此预制件部署到 AI 平台后，用户可以通过自然语言调用这些功能：

**用户**: "把这个视频的前30秒转换成 mp3"  
**AI**: *调用 `video_to_audio` 和 `trim_video`*

**用户**: "把这三个视频拼接在一起"  
**AI**: *调用 `concatenate_videos`*

**用户**: "把这个视频压缩到原来的一半大小"  
**AI**: *调用 `resize_video` with `scale=0.5`*

---

## 技术细节

- **编码格式**: 输出视频使用 H.264 (libx264) 编码，音频使用 AAC 编码
- **依赖**: MoviePy >= 2.2.1
- **平台**: 支持 macOS、Linux、Windows
- **Python**: 要求 Python 3.11+

---

## 许可证

MIT License

