"""
视频处理预制件核心模块

使用 moviepy 实现常见的视频处理功能，包括：
- 视频转音频
- 视频拼接
- 视频剪辑
- 视频调整大小
- 提取视频片段

所有暴露给 AI 的函数都必须在此文件中定义。
"""

import os
from typing import Optional
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


def video_to_audio(
    video_path: str,
    output_path: Optional[str] = None,
    audio_format: str = "mp3",
    audio_bitrate: str = "192k"
) -> dict:
    """
    将视频文件转换为音频文件

    Args:
        video_path: 输入视频文件路径（InputFile 类型）
        output_path: 输出音频文件路径（可选，如果不提供则自动生成）
        audio_format: 音频格式（mp3, wav, aac, flac 等），默认为 mp3
        audio_bitrate: 音频比特率，默认为 192k

    Returns:
        包含转换结果的字典，格式为：
        {
            "success": bool,
            "output_file": str,      # 输出文件路径（成功时）
            "format": str,           # 音频格式（成功时）
            "duration": float,       # 音频时长（秒）（成功时）
            "error": str,            # 错误信息（失败时）
            "error_code": str        # 错误代码（失败时）
        }

    Examples:
        >>> video_to_audio("input.mp4")
        {'success': True, 'output_file': 'input.mp3', 'format': 'mp3', 'duration': 120.5}
    """
    try:
        # 验证输入文件
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"视频文件不存在: {video_path}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = f"{base_name}.{audio_format}"

        # 加载视频并提取音频
        video = VideoFileClip(video_path)

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
        # 某些格式（如 aac）需要明确指定 codec
        codec_map = {
            "aac": "aac",
            "m4a": "aac"
        }
        codec = codec_map.get(audio_format.lower())

        video.audio.write_audiofile(
            output_path,
            bitrate=audio_bitrate,
            codec=codec,
            logger="bar"  # 显示进度条
        )

        # 关闭视频文件
        video.close()

        return {
            "success": True,
            "output_file": output_path,
            "format": audio_format,
            "duration": duration
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "CONVERSION_ERROR"
        }


def concatenate_videos(
    video_paths: list,
    output_path: Optional[str] = None,
    transition: Optional[str] = None
) -> dict:
    """
    拼接多个视频文件

    Args:
        video_paths: 要拼接的视频文件路径列表
        output_path: 输出视频文件路径（可选，如果不提供则自动生成）
        transition: 转场效果（暂不支持，预留参数）

    Returns:
        包含拼接结果的字典，格式为：
        {
            "success": bool,
            "output_file": str,      # 输出文件路径（成功时）
            "total_duration": float, # 总时长（秒）（成功时）
            "video_count": int,      # 拼接的视频数量（成功时）
            "error": str,            # 错误信息（失败时）
            "error_code": str        # 错误代码（失败时）
        }

    Examples:
        >>> concatenate_videos(["video1.mp4", "video2.mp4", "video3.mp4"])
        {'success': True, 'output_file': 'output.mp4', 'total_duration': 300.5, 'video_count': 3}
    """
    try:
        # 验证输入
        if not video_paths or len(video_paths) < 2:
            return {
                "success": False,
                "error": "至少需要提供两个视频文件进行拼接",
                "error_code": "INSUFFICIENT_VIDEOS"
            }

        # 验证所有文件存在
        for video_path in video_paths:
            if not os.path.exists(video_path):
                return {
                    "success": False,
                    "error": f"视频文件不存在: {video_path}",
                    "error_code": "FILE_NOT_FOUND"
                }

        # 生成输出路径
        if output_path is None:
            output_path = "concatenated_output.mp4"

        # 加载所有视频
        clips = [VideoFileClip(path) for path in video_paths]

        # 拼接视频
        final_clip = concatenate_videoclips(clips, method="compose")
        total_duration = final_clip.duration

        # 写入输出文件
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger="bar"  # 显示进度条
        )

        # 关闭所有视频
        for clip in clips:
            clip.close()
        final_clip.close()

        return {
            "success": True,
            "output_file": output_path,
            "total_duration": total_duration,
            "video_count": len(video_paths)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "CONCATENATION_ERROR"
        }


def trim_video(
    video_path: str,
    start_time: float,
    end_time: float,
    output_path: Optional[str] = None
) -> dict:
    """
    剪辑视频，提取指定时间段的内容

    Args:
        video_path: 输入视频文件路径
        start_time: 开始时间（秒）
        end_time: 结束时间（秒）
        output_path: 输出视频文件路径（可选）

    Returns:
        包含剪辑结果的字典，格式为：
        {
            "success": bool,
            "output_file": str,      # 输出文件路径（成功时）
            "duration": float,       # 剪辑后的时长（秒）（成功时）
            "start_time": float,     # 开始时间（成功时）
            "end_time": float,       # 结束时间（成功时）
            "error": str,            # 错误信息（失败时）
            "error_code": str        # 错误代码（失败时）
        }

    Examples:
        >>> trim_video("input.mp4", 10, 30)
        {'success': True, 'output_file': 'input_trimmed.mp4', 'duration': 20.0, 'start_time': 10, 'end_time': 30}
    """
    try:
        # 验证输入文件
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"视频文件不存在: {video_path}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 验证时间参数
        if start_time < 0:
            return {
                "success": False,
                "error": "开始时间不能为负数",
                "error_code": "INVALID_START_TIME"
            }

        if end_time <= start_time:
            return {
                "success": False,
                "error": "结束时间必须大于开始时间",
                "error_code": "INVALID_TIME_RANGE"
            }

        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = f"{base_name}_trimmed.mp4"

        # 加载视频并剪辑
        video = VideoFileClip(video_path)

        # 检查时间范围
        if end_time > video.duration:
            video.close()
            return {
                "success": False,
                "error": f"结束时间 ({end_time}s) 超出视频长度 ({video.duration}s)",
                "error_code": "TIME_OUT_OF_RANGE"
            }

        # 提取子片段
        trimmed_clip = video.subclipped(start_time, end_time)
        duration = trimmed_clip.duration

        # 写入输出文件
        trimmed_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger="bar"  # 显示进度条
        )

        # 关闭视频
        video.close()
        trimmed_clip.close()

        return {
            "success": True,
            "output_file": output_path,
            "duration": duration,
            "start_time": start_time,
            "end_time": end_time
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "TRIM_ERROR"
        }


def resize_video(
    video_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: Optional[float] = None,
    output_path: Optional[str] = None
) -> dict:
    """
    调整视频尺寸

    可以通过指定宽度/高度或缩放比例来调整视频大小。
    如果只指定宽度或高度，将保持原始宽高比。

    Args:
        video_path: 输入视频文件路径
        width: 目标宽度（像素），可选
        height: 目标高度（像素），可选
        scale: 缩放比例（如 0.5 表示缩小到原来的 50%），可选
        output_path: 输出视频文件路径（可选）

    Returns:
        包含调整结果的字典，格式为：
        {
            "success": bool,
            "output_file": str,      # 输出文件路径（成功时）
            "original_size": dict,   # 原始尺寸 {"width": int, "height": int}（成功时）
            "new_size": dict,        # 新尺寸 {"width": int, "height": int}（成功时）
            "error": str,            # 错误信息（失败时）
            "error_code": str        # 错误代码（失败时）
        }

    Examples:
        >>> resize_video("input.mp4", width=1280)
        {'success': True, 'output_file': 'input_resized.mp4', ...}

        >>> resize_video("input.mp4", scale=0.5)
        {'success': True, 'output_file': 'input_resized.mp4', ...}
    """
    try:
        # 验证输入文件
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"视频文件不存在: {video_path}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 验证参数
        if width is None and height is None and scale is None:
            return {
                "success": False,
                "error": "必须指定 width、height 或 scale 中的至少一个参数",
                "error_code": "MISSING_SIZE_PARAMETER"
            }

        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = f"{base_name}_resized.mp4"

        # 加载视频
        video = VideoFileClip(video_path)
        original_size = {"width": video.w, "height": video.h}

        # 调整大小
        if scale is not None:
            # 使用缩放比例
            resized_clip = video.resized(scale)
        elif width is not None and height is not None:
            # 同时指定宽度和高度
            resized_clip = video.resized(new_size=(width, height))
        elif width is not None:
            # 只指定宽度，保持宽高比
            resized_clip = video.resized(width=width)
        else:
            # 只指定高度，保持宽高比
            resized_clip = video.resized(height=height)

        new_size = {"width": resized_clip.w, "height": resized_clip.h}

        # 写入输出文件
        resized_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger="bar"  # 显示进度条
        )

        # 关闭视频
        video.close()
        resized_clip.close()

        return {
            "success": True,
            "output_file": output_path,
            "original_size": original_size,
            "new_size": new_size
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "RESIZE_ERROR"
        }


def extract_audio_segment(
    audio_path: str,
    start_time: float,
    end_time: float,
    output_path: Optional[str] = None
) -> dict:
    """
    从音频文件中提取指定时间段

    Args:
        audio_path: 输入音频文件路径
        start_time: 开始时间（秒）
        end_time: 结束时间（秒）
        output_path: 输出音频文件路径（可选）

    Returns:
        包含提取结果的字典，格式为：
        {
            "success": bool,
            "output_file": str,      # 输出文件路径（成功时）
            "duration": float,       # 提取的音频时长（秒）（成功时）
            "start_time": float,     # 开始时间（成功时）
            "end_time": float,       # 结束时间（成功时）
            "error": str,            # 错误信息（失败时）
            "error_code": str        # 错误代码（失败时）
        }

    Examples:
        >>> extract_audio_segment("audio.mp3", 5, 15)
        {'success': True, 'output_file': 'audio_segment.mp3', 'duration': 10.0, ...}
    """
    try:
        # 验证输入文件
        if not os.path.exists(audio_path):
            return {
                "success": False,
                "error": f"音频文件不存在: {audio_path}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 验证时间参数
        if start_time < 0:
            return {
                "success": False,
                "error": "开始时间不能为负数",
                "error_code": "INVALID_START_TIME"
            }

        if end_time <= start_time:
            return {
                "success": False,
                "error": "结束时间必须大于开始时间",
                "error_code": "INVALID_TIME_RANGE"
            }

        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            ext = os.path.splitext(audio_path)[1]
            output_path = f"{base_name}_segment{ext}"

        # 加载音频并提取片段
        audio = AudioFileClip(audio_path)

        # 检查时间范围
        if end_time > audio.duration:
            audio.close()
            return {
                "success": False,
                "error": f"结束时间 ({end_time}s) 超出音频长度 ({audio.duration}s)",
                "error_code": "TIME_OUT_OF_RANGE"
            }

        # 提取子片段
        segment = audio.subclipped(start_time, end_time)
        duration = segment.duration

        # 写入输出文件
        segment.write_audiofile(output_path, logger="bar")  # 显示进度条

        # 关闭音频
        audio.close()
        segment.close()

        return {
            "success": True,
            "output_file": output_path,
            "duration": duration,
            "start_time": start_time,
            "end_time": end_time
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "EXTRACT_ERROR"
        }


def get_video_info(video_path: str) -> dict:
    """
    获取视频文件的详细信息

    Args:
        video_path: 视频文件路径

    Returns:
        包含视频信息的字典，格式为：
        {
            "success": bool,
            "info": dict,            # 视频信息（成功时）
            "error": str,            # 错误信息（失败时）
            "error_code": str        # 错误代码（失败时）
        }

    Examples:
        >>> get_video_info("video.mp4")
        {'success': True, 'info': {'duration': 120.5, 'fps': 30, 'size': [1920, 1080], ...}}
    """
    try:
        # 验证输入文件
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"视频文件不存在: {video_path}",
                "error_code": "FILE_NOT_FOUND"
            }

        # 加载视频
        video = VideoFileClip(video_path)

        # 获取文件大小
        file_size = os.path.getsize(video_path)

        info = {
            "duration": video.duration,
            "fps": video.fps,
            "size": [video.w, video.h],
            "width": video.w,
            "height": video.h,
            "has_audio": video.audio is not None,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2)
        }

        # 关闭视频
        video.close()

        return {
            "success": True,
            "info": info
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "INFO_ERROR"
        }
