"""
视频处理预制件

基于 MoviePy 的视频处理工具集
"""

from .main import (
    video_to_audio,
    concatenate_videos,
    trim_video,
    resize_video,
    extract_audio_segment,
    get_video_info
)

__all__ = [
    "video_to_audio",
    "concatenate_videos",
    "trim_video",
    "resize_video",
    "extract_audio_segment",
    "get_video_info"
]

__version__ = "0.1.0"
