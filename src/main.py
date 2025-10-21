"""
视频处理预制件核心模块

使用 moviepy 实现常见的视频处理功能，包括：
- 视频转音频
- 视频拼接
- 视频剪辑
- 视频调整大小
- 提取视频片段

约定：
- 输入文件：data/inputs/<文件名>
- 输出文件：data/outputs/<文件名>
- 所有文件参数都是列表形式（即使只有一个文件）
"""

from pathlib import Path
from typing import List, Optional
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


# 固定路径
DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")


def _input_path(filename: str) -> Path:
    """获取输入文件路径"""
    return DATA_INPUTS / filename


def _output_path(filename: str) -> Path:
    """获取输出文件路径（自动创建目录）"""
    DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
    return DATA_OUTPUTS / filename


def video_to_audio(
    input_files: List[str],
    audio_format: str = "mp3",
    audio_bitrate: str = "192k"
) -> dict:
    """
    将视频文件转换为音频文件

    Args:
        input_files: 输入视频文件名列表（只取第一个）
        audio_format: 音频格式（mp3, wav, aac, flac 等），默认为 mp3
        audio_bitrate: 音频比特率，默认为 192k

    Returns:
        包含转换结果的字典
    """
    try:
        # 取第一个文件
        video_filename = input_files[0]
        video_path = _input_path(video_filename)

        # 验证输入文件
        if not video_path.exists():
            return {
                "success": False,
                "error": f"视频文件不存在: {video_filename}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 生成输出路径
        output_filename = f"audio.{audio_format}"
        output_path = _output_path(output_filename)

        # 加载视频并提取音频
        video = VideoFileClip(str(video_path))

        # 检查视频是否有音频轨道
        if video.audio is None:
            video.close()
            return {
                "success": False,
                "error": "视频文件不包含音频轨道",
                "error_code": "NO_AUDIO_TRACK"
            }

        duration = video.duration

        # 提取音频并保存
        codec_map = {"aac": "aac", "m4a": "aac"}
        codec = codec_map.get(audio_format.lower())

        video.audio.write_audiofile(
            str(output_path),
            bitrate=audio_bitrate,
            codec=codec,
            logger="bar"
        )

        video.close()

        return {
            "success": True,
            "output_file": f"data/outputs/{output_filename}",
            "format": audio_format,
            "duration": duration
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def concatenate_videos(
    input_files: List[str],
    output_format: str = "mp4",
    method: str = "compose"
) -> dict:
    """
    拼接多个视频文件

    Args:
        input_files: 输入视频文件名列表（至少2个）
        output_format: 输出视频格式，默认 mp4
        method: 拼接方法（compose 或 chain），默认 compose

    Returns:
        包含拼接结果的字典
    """
    try:
        if len(input_files) < 2:
            return {
                "success": False,
                "error": "至少需要2个视频文件进行拼接",
                "error_code": "INSUFFICIENT_FILES"
            }

        # 加载所有视频
        clips = []
        total_duration = 0

        for filename in input_files:
            video_path = _input_path(filename)
            if not video_path.exists():
                return {
                    "success": False,
                    "error": f"视频文件不存在: {filename}",
                    "error_code": "FILE_NOT_FOUND"
                }

            clip = VideoFileClip(str(video_path))
            clips.append(clip)
            total_duration += clip.duration

        # 拼接视频
        final_clip = concatenate_videoclips(clips, method=method)

        # 输出
        output_filename = f"result.{output_format}"
        output_path = _output_path(output_filename)

        final_clip.write_videofile(str(output_path), logger="bar")

        # 清理
        for clip in clips:
            clip.close()
        final_clip.close()

        return {
            "success": True,
            "output_file": f"data/outputs/{output_filename}",
            "input_count": len(input_files),
            "total_duration": total_duration
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def trim_video(
    input_files: List[str],
    start_time: float,
    end_time: Optional[float] = None,
    output_format: str = "mp4"
) -> dict:
    """
    剪辑视频片段

    Args:
        input_files: 输入视频文件名列表（只取第一个）
        start_time: 开始时间（秒）
        end_time: 结束时间（秒），如果不提供则到视频结尾
        output_format: 输出格式，默认 mp4

    Returns:
        包含剪辑结果的字典
    """
    try:
        video_filename = input_files[0]
        video_path = _input_path(video_filename)

        if not video_path.exists():
            return {
                "success": False,
                "error": f"视频文件不存在: {video_filename}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 加载视频
        video = VideoFileClip(str(video_path))

        # 验证时间范围
        if start_time < 0:
            start_time = 0
        if end_time is None or end_time > video.duration:
            end_time = video.duration
        if start_time >= end_time:
            video.close()
            return {
                "success": False,
                "error": f"开始时间 ({start_time}s) 必须小于结束时间 ({end_time}s)",
                "error_code": "INVALID_TIME_RANGE"
            }

        # 剪辑
        trimmed = video.subclipped(start_time, end_time)

        # 输出
        output_filename = f"trimmed.{output_format}"
        output_path = _output_path(output_filename)

        trimmed.write_videofile(str(output_path), logger="bar")

        duration = trimmed.duration

        # 清理
        video.close()
        trimmed.close()

        return {
            "success": True,
            "output_file": f"data/outputs/{output_filename}",
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def resize_video(
    input_files: List[str],
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: Optional[float] = None,
    output_format: str = "mp4"
) -> dict:
    """
    调整视频尺寸

    Args:
        input_files: 输入视频文件名列表（只取第一个）
        width: 目标宽度（像素），如果只提供宽度则按比例缩放
        height: 目标高度（像素），如果只提供高度则按比例缩放
        scale: 缩放比例（如 0.5 表示缩小一半），优先级低于 width/height
        output_format: 输出格式，默认 mp4

    Returns:
        包含调整结果的字典
    """
    try:
        video_filename = input_files[0]
        video_path = _input_path(video_filename)

        if not video_path.exists():
            return {
                "success": False,
                "error": f"视频文件不存在: {video_filename}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 加载视频
        video = VideoFileClip(str(video_path))
        original_size = video.size  # (width, height)

        # 确定目标尺寸
        if width and height:
            new_size = (width, height)
        elif width:
            # 按宽度等比缩放
            ratio = width / original_size[0]
            new_size = (width, int(original_size[1] * ratio))
        elif height:
            # 按高度等比缩放
            ratio = height / original_size[1]
            new_size = (int(original_size[0] * ratio), height)
        elif scale:
            # 按比例缩放
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        else:
            video.close()
            return {
                "success": False,
                "error": "必须提供 width, height 或 scale 参数之一",
                "error_code": "MISSING_PARAMETERS"
            }

        # 调整大小
        resized = video.resized(new_size)

        # 输出
        output_filename = f"resized.{output_format}"
        output_path = _output_path(output_filename)

        resized.write_videofile(str(output_path), logger="bar")

        # 清理
        video.close()
        resized.close()

        return {
            "success": True,
            "output_file": f"data/outputs/{output_filename}",
            "original_size": original_size,
            "new_size": new_size
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def extract_frames(
    input_files: List[str],
    times: List[float],
    output_format: str = "jpg"
) -> dict:
    """
    从视频提取帧

    Args:
        input_files: 输入视频文件名列表（只取第一个）
        times: 要提取的时间点列表（秒）
        output_format: 输出图片格式，默认 jpg

    Returns:
        包含提取结果的字典
    """
    try:
        video_filename = input_files[0]
        video_path = _input_path(video_filename)

        if not video_path.exists():
            return {
                "success": False,
                "error": f"视频文件不存在: {video_filename}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 加载视频
        video = VideoFileClip(str(video_path))

        # 提取帧
        frame_files = []
        for i, t in enumerate(times):
            if t < 0 or t > video.duration:
                continue

            frame = video.get_frame(t)

            # 保存帧
            output_filename = f"frame_{i:03d}.{output_format}"
            output_path = _output_path(output_filename)

            from PIL import Image
            img = Image.fromarray(frame)
            img.save(str(output_path))

            frame_files.append(f"data/outputs/{output_filename}")

        video.close()

        return {
            "success": True,
            "frame_count": len(frame_files),
            "frames": frame_files
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }
