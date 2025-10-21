"""
视频处理预制件核心逻辑 (v3.0 架构)

所有函数：
- 不再接收文件参数
- 自动扫描 data/inputs/{file_key}/ 目录
- 写入 data/outputs/
- 返回业务结果（不包含文件路径）
"""
from pathlib import Path
from typing import Optional
from moviepy import VideoFileClip, concatenate_videoclips, ImageClip

# 固定路径约定
DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")


def video_to_audio(
    audio_format: str = "mp3",
    audio_bitrate: str = "192k"
) -> dict:
    """
    将视频文件转换为音频文件（v3.0 架构）

    Args:
        audio_format: 音频格式（mp3, wav, aac, flac 等）
        audio_bitrate: 音频比特率

    Returns:
        转换结果（不包含文件路径）
    """
    try:
        # 扫描输入目录
        input_files = list((DATA_INPUTS / "input").glob("*"))
        if not input_files:
            return {
                "success": False,
                "error": "未找到输入视频文件",
                "error_code": "NO_INPUT_FILE"
            }

        video_path = input_files[0]

        # 加载视频
        video = VideoFileClip(str(video_path))

        if video.audio is None:
            video.close()
            return {
                "success": False,
                "error": "视频文件不包含音频轨道",
                "error_code": "NO_AUDIO_TRACK"
            }

        duration = video.duration

        # 输出文件
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
        output_path = DATA_OUTPUTS / f"audio.{audio_format}"

        # 提取音频
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
    output_format: str = "mp4",
    method: str = "compose"
) -> dict:
    """
    拼接多个视频文件（v3.0 架构）

    Args:
        output_format: 输出视频格式
        method: 拼接方法（compose 或 chain）

    Returns:
        拼接结果（不包含文件路径）
    """
    try:
        # 扫描输入目录
        input_files = list((DATA_INPUTS / "input").glob("*"))
        if len(input_files) < 2:
            return {
                "success": False,
                "error": "至少需要2个视频文件进行拼接",
                "error_code": "INSUFFICIENT_FILES"
            }

        # 加载所有视频
        clips = []
        total_duration = 0

        for video_path in input_files:
            clip = VideoFileClip(str(video_path))
            clips.append(clip)
            total_duration += clip.duration

        # 拼接视频
        if method == "compose":
            final_clip = concatenate_videoclips(clips, method="compose")
        elif method == "chain":
            final_clip = concatenate_videoclips(clips, method="chain")
        else:
            for clip in clips:
                clip.close()
            return {
                "success": False,
                "error": f"不支持的拼接方法: {method}",
                "error_code": "INVALID_METHOD"
            }

        # 输出
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
        output_path = DATA_OUTPUTS / f"concatenated.{output_format}"

        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            logger="bar"
        )

        # 关闭所有
        final_clip.close()
        for clip in clips:
            clip.close()

        return {
            "success": True,
            "count": len(input_files),
            "total_duration": total_duration,
            "method": method
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def trim_video(
    start_time: float,
    end_time: Optional[float] = None,
    output_format: str = "mp4"
) -> dict:
    """
    剪辑视频（v3.0 架构）

    Args:
        start_time: 开始时间（秒）
        end_time: 结束时间（秒，可选）
        output_format: 输出格式

    Returns:
        剪辑结果（不包含文件路径）
    """
    try:
        # 扫描输入
        input_files = list((DATA_INPUTS / "input").glob("*"))
        if not input_files:
            return {
                "success": False,
                "error": "未找到输入视频文件",
                "error_code": "NO_INPUT_FILE"
            }

        video_path = input_files[0]
        video = VideoFileClip(str(video_path))

        # 剪辑
        trimmed = video.subclipped(start_time, end_time)

        # 输出
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
        output_path = DATA_OUTPUTS / f"trimmed.{output_format}"

        trimmed.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            logger="bar"
        )

        duration = trimmed.duration
        video.close()
        trimmed.close()

        return {
            "success": True,
            "start_time": start_time,
            "end_time": end_time or video.duration,
            "duration": duration
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def resize_video(
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: Optional[float] = None,
    output_format: str = "mp4"
) -> dict:
    """
    调整视频尺寸（v3.0 架构）

    Args:
        width: 目标宽度（像素）
        height: 目标高度（像素）
        scale: 缩放比例（如 0.5 表示缩小到原来的一半）
        output_format: 输出格式

    Returns:
        调整结果（不包含文件路径）
    """
    try:
        if not any([width, height, scale]):
            return {
                "success": False,
                "error": "必须提供 width, height 或 scale 中的至少一个参数",
                "error_code": "MISSING_PARAMETERS"
            }

        # 扫描输入
        input_files = list((DATA_INPUTS / "input").glob("*"))
        if not input_files:
            return {
                "success": False,
                "error": "未找到输入视频文件",
                "error_code": "NO_INPUT_FILE"
            }

        video_path = input_files[0]
        video = VideoFileClip(str(video_path))

        original_width, original_height = video.size

        # 计算新尺寸
        if scale:
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
        elif width and height:
            new_width, new_height = width, height
        elif width:
            ratio = width / original_width
            new_width = width
            new_height = int(original_height * ratio)
        else:  # height
            ratio = height / original_height
            new_width = int(original_width * ratio)
            new_height = height

        # 调整尺寸
        resized = video.resized((new_width, new_height))

        # 输出
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
        output_path = DATA_OUTPUTS / f"resized.{output_format}"

        resized.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            logger="bar"
        )

        video.close()
        resized.close()

        return {
            "success": True,
            "original_width": original_width,
            "original_height": original_height,
            "new_width": new_width,
            "new_height": new_height
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }


def extract_frames(
    times: list,
    image_format: str = "png"
) -> dict:
    """
    从视频中提取指定时间点的帧（v3.0 架构）

    Args:
        times: 要提取的时间点列表（秒）
        image_format: 图片格式

    Returns:
        提取结果（不包含文件路径）
    """
    try:
        if not times or not isinstance(times, list):
            return {
                "success": False,
                "error": "times 参数必须是非空列表",
                "error_code": "INVALID_TIMES"
            }

        # 扫描输入
        input_files = list((DATA_INPUTS / "input").glob("*"))
        if not input_files:
            return {
                "success": False,
                "error": "未找到输入视频文件",
                "error_code": "NO_INPUT_FILE"
            }

        video_path = input_files[0]
        video = VideoFileClip(str(video_path))

        # 输出目录
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        # 提取每个时间点的帧
        extracted_count = 0
        for i, t in enumerate(times):
            if t < 0 or t > video.duration:
                continue

            frame = video.get_frame(t)
            output_path = DATA_OUTPUTS / f"frame_{i+1:03d}.{image_format}"

            img = ImageClip(frame)
            img.save_frame(str(output_path))
            img.close()
            extracted_count += 1

        video.close()

        return {
            "success": True,
            "requested_count": len(times),
            "extracted_count": extracted_count,
            "format": image_format
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESSING_ERROR"
        }

