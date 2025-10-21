"""
视频处理预制件

基于 MoviePy 的视频处理工具集
"""

from .main import (
    video_to_audio,
    concatenate_videos,
    trim_video,
    resize_video,
    extract_frames
)

__all__ = [
    "video_to_audio",
    "concatenate_videos",
    "trim_video",
    "resize_video",
    "extract_frames"
]

__version__ = "0.2.0"
