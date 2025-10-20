# Prefab 文件处理指南

> 针对使用 InputFile/OutputFile 的 Prefab 开发者

## 📁 工作目录结构

当你的 Prefab 函数被调用时，Gateway 会为每个请求创建独立的工作目录：

```
/mnt/prefab-workspace/{request_id}/
├── inputs/          # InputFile 自动下载到这里
│   ├── video.mp4   # 参数名: video
│   └── config.json # 参数名: config
└── outputs/         # 建议把 OutputFile 放这里
    └── result.mp4  # 你创建的输出文件
```

## 🔍 接收输入文件（InputFile）

### 1. 函数定义

```python
# src/main.py
def process_video(video: str, format: str = "mp4") -> dict:
    """
    处理视频文件
    
    Args:
        video: 输入视频文件路径 (InputFile)
        format: 输出格式
    """
    # video 参数会接收到完整的本地路径
    # 例如: "/mnt/prefab-workspace/abc-123/inputs/video.mp4"
```

### 2. Manifest 声明

```json
{
  "functions": [{
    "name": "process_video",
    "parameters": {
      "video": {
        "type": "InputFile",
        "description": "输入视频文件"
      }
    }
  }]
}
```

### 3. 使用输入文件

```python
from pathlib import Path

def process_video(video: str, format: str = "mp4") -> dict:
    # 直接使用路径
    video_path = Path(video)
    
    if not video_path.exists():
        return {"success": False, "error": "Input file not found"}
    
    # 读取文件
    with open(video_path, 'rb') as f:
        data = f.read()
    
    # 处理...
```

## 📤 生成输出文件（OutputFile）

### ⚠️ 重要：输出文件路径规范

**推荐做法**：从请求中获取 `outputs_dir`，把文件放到那里

```python
def process_video(video: str, request: dict = None) -> dict:
    """
    Args:
        video: 输入视频 (InputFile)
        request: 运行时注入的请求上下文（包含 _workspace 信息）
    """
    # 方式1: 使用推荐的输出目录（推荐）
    if request and "_workspace" in request:
        outputs_dir = Path(request["_workspace"]["outputs_dir"])
    else:
        # 方式2: 兜底逻辑 - 使用输入文件的父目录的 outputs 子目录
        outputs_dir = Path(video).parent.parent / "outputs"
    
    # 确保输出目录存在
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成输出文件
    output_file = outputs_dir / "result.mp4"
    
    # 处理并保存...
    with open(output_file, 'wb') as f:
        f.write(processed_data)
    
    # 返回输出文件的完整路径
    return {
        "success": True,
        "output_video": str(output_file)
    }
```

### Manifest 声明

```json
{
  "functions": [{
    "name": "process_video",
    "returns": {
      "type": "object",
      "properties": {
        "success": {"type": "boolean"},
        "output_video": {
          "type": "OutputFile",
          "description": "处理后的视频文件"
        }
      }
    }
  }]
}
```

## 🎯 最佳实践

### 1. 文件命名规范

```python
import uuid
from pathlib import Path
from datetime import datetime

def generate_output_filename(input_path: str, suffix: str = "") -> str:
    """生成唯一的输出文件名"""
    input_file = Path(input_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    # 保留扩展名
    ext = input_file.suffix
    name = input_file.stem
    
    return f"{name}_{suffix}_{timestamp}_{unique_id}{ext}"
```

### 2. 错误处理

```python
def process_video(video: str, request: dict = None) -> dict:
    try:
        video_path = Path(video)
        
        # 验证输入文件
        if not video_path.exists():
            return {
                "success": False,
                "error": f"Input file not found: {video}",
                "error_code": "FILE_NOT_FOUND"
            }
        
        # 获取输出目录
        outputs_dir = Path(request["_workspace"]["outputs_dir"])
        output_file = outputs_dir / "result.mp4"
        
        # 处理...
        
        # 验证输出文件已创建
        if not output_file.exists():
            return {
                "success": False,
                "error": "Failed to create output file"
            }
        
        return {
            "success": True,
            "output_video": str(output_file)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }
```

### 3. 临时文件清理

```python
import tempfile
import shutil

def process_video(video: str, request: dict = None) -> dict:
    # 使用系统临时目录处理中间文件
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 处理中间文件
        intermediate_file = temp_path / "intermediate.mp4"
        # ... 处理 ...
        
        # 最终结果保存到 outputs 目录
        outputs_dir = Path(request["_workspace"]["outputs_dir"])
        final_output = outputs_dir / "result.mp4"
        shutil.copy(intermediate_file, final_output)
        
        # temp_dir 会自动清理
    
    return {"success": True, "output_video": str(final_output)}
```

## 🔄 完整示例

```python
# src/main.py
from pathlib import Path
from typing import Dict, Any

def video_to_gif(
    video: str,
    start_time: float = 0.0,
    duration: float = 3.0,
    request: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    将视频转换为 GIF
    
    Args:
        video: 输入视频文件 (InputFile)
        start_time: 起始时间（秒）
        duration: 持续时间（秒）
        request: 运行时上下文（自动注入）
    
    Returns:
        包含 output_gif (OutputFile) 的结果
    """
    try:
        # 1. 验证输入
        video_path = Path(video)
        if not video_path.exists():
            return {
                "success": False,
                "error": f"Video file not found: {video}"
            }
        
        # 2. 获取输出目录
        if request and "_workspace" in request:
            outputs_dir = Path(request["_workspace"]["outputs_dir"])
        else:
            # 兜底逻辑
            outputs_dir = video_path.parent.parent / "outputs"
        
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. 生成输出文件名
        output_gif = outputs_dir / f"{video_path.stem}.gif"
        
        # 4. 处理视频（示例：使用 moviepy）
        from moviepy.editor import VideoFileClip
        
        clip = VideoFileClip(str(video_path))
        clip = clip.subclip(start_time, start_time + duration)
        clip.write_gif(str(output_gif), fps=10)
        clip.close()
        
        # 5. 返回结果
        return {
            "success": True,
            "output_gif": str(output_gif),
            "duration": duration
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

对应的 `prefab-manifest.json`:

```json
{
  "id": "video-to-gif",
  "name": "视频转 GIF",
  "version": "1.0.0",
  "functions": [
    {
      "name": "video_to_gif",
      "description": "将视频转换为 GIF 动图",
      "parameters": {
        "video": {
          "type": "InputFile",
          "description": "输入视频文件"
        },
        "start_time": {
          "type": "number",
          "description": "起始时间（秒）",
          "default": 0.0
        },
        "duration": {
          "type": "number",
          "description": "持续时间（秒）",
          "default": 3.0
        }
      },
      "returns": {
        "type": "object",
        "properties": {
          "success": {"type": "boolean"},
          "output_gif": {
            "type": "OutputFile",
            "description": "输出的 GIF 文件"
          },
          "duration": {"type": "number"}
        }
      }
    }
  ]
}
```

## ❓ 常见问题

### Q1: 我可以在任意路径创建输出文件吗？

**A**: 技术上可以，但**强烈建议**使用 `_workspace.outputs_dir`。原因：
- Gateway 会自动清理 workspace 目录
- 其他路径可能没有写权限
- 遵循规范便于调试和维护

### Q2: 输入文件会被自动删除吗？

**A**: 是的，Gateway 在上传完 OutputFile 后会清理整个 workspace（包括 inputs/）。你的 Prefab 不需要手动清理。

### Q3: 如果我的函数没有 `request` 参数怎么办？

**A**: Runtime Handler 目前不会自动注入 `request`。你需要：
1. 在函数签名中添加 `request: dict = None` 参数
2. 使用兜底逻辑（从 input 文件路径推断 outputs 目录）

### Q4: 我可以返回多个 OutputFile 吗？

**A**: 可以！在返回值中声明多个 OutputFile 字段即可：

```python
return {
    "success": True,
    "video_output": str(output_video),
    "thumbnail": str(thumbnail_file),
    "metadata": str(metadata_json)
}
```

```json
{
  "returns": {
    "properties": {
      "video_output": {"type": "OutputFile"},
      "thumbnail": {"type": "OutputFile"},
      "metadata": {"type": "OutputFile"}
    }
  }
}
```

## 📚 参考资料

- [Prefab 开发指南](../Prefab-Template/AGENTS.md)
- [文件处理架构](../prefab-gateway/FILE_HANDLING_SETUP.md)
- [Runtime Handler 源码](runtime/handler.py)

