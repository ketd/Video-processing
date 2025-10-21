"""
基础功能测试（v3.0 架构）

测试新架构下的视频处理函数
"""
import os
import sys
import pytest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import (
    video_to_audio,
    concatenate_videos,
    trim_video,
    resize_video,
    extract_frames
)


class TestBasicFunctions:
    """测试基础功能（v3.0 架构）"""

    def test_video_to_audio_no_input(self):
        """测试没有输入文件"""
        # v3.0: 不传文件参数，函数自动扫描
        # 由于没有创建输入文件，应该返回错误
        result = video_to_audio(audio_format="mp3")
        assert result["success"] is False
        assert result["error_code"] == "NO_INPUT_FILE"

    def test_concatenate_videos_insufficient_files(self):
        """测试视频数量不足"""
        # v3.0: 函数自动扫描，需要至少2个文件
        result = concatenate_videos()
        assert result["success"] is False
        assert result["error_code"] in ["INSUFFICIENT_FILES", "NO_INPUT_FILE"]

    def test_trim_video_no_input(self):
        """测试剪辑视频无输入"""
        result = trim_video(start_time=0, end_time=10)
        assert result["success"] is False
        assert result["error_code"] == "NO_INPUT_FILE"

    def test_resize_video_no_input(self):
        """测试调整大小无输入"""
        result = resize_video(width=640)
        assert result["success"] is False
        assert result["error_code"] == "NO_INPUT_FILE"

    def test_resize_video_missing_parameters(self):
        """测试缺少必需参数"""
        result = resize_video()
        assert result["success"] is False
        assert result["error_code"] == "MISSING_PARAMETERS"

    def test_extract_frames_no_input(self):
        """测试提取帧无输入"""
        result = extract_frames(times=[1.0, 2.0])
        assert result["success"] is False
        assert result["error_code"] == "NO_INPUT_FILE"

    def test_extract_frames_invalid_times(self):
        """测试无效的时间参数"""
        result = extract_frames(times=None)
        assert result["success"] is False
        assert result["error_code"] == "INVALID_TIMES"


class TestPathConventions:
    """测试路径约定"""

    def test_input_path_convention(self):
        """测试输入路径约定"""
        from src.main import DATA_INPUTS
        assert str(DATA_INPUTS) == "data/inputs"

    def test_output_path_convention(self):
        """测试输出路径约定"""
        from src.main import DATA_OUTPUTS
        assert str(DATA_OUTPUTS) == "data/outputs"


class TestFunctionSignatures:
    """测试函数签名（v3.0 架构）"""

    def test_video_to_audio_no_file_params(self):
        """确保 video_to_audio 不接收文件参数"""
        import inspect
        sig = inspect.signature(video_to_audio)
        
        # v3.0: 应该只有业务参数
        assert 'input_files' not in sig.parameters
        assert 'audio_format' in sig.parameters
        assert 'audio_bitrate' in sig.parameters

    def test_concatenate_videos_no_file_params(self):
        """确保 concatenate_videos 不接收文件参数"""
        import inspect
        sig = inspect.signature(concatenate_videos)
        
        assert 'input_files' not in sig.parameters
        assert 'output_format' in sig.parameters
        assert 'method' in sig.parameters

    def test_trim_video_no_file_params(self):
        """确保 trim_video 不接收文件参数"""
        import inspect
        sig = inspect.signature(trim_video)
        
        assert 'input_files' not in sig.parameters
        assert 'start_time' in sig.parameters
        assert 'end_time' in sig.parameters

    def test_resize_video_no_file_params(self):
        """确保 resize_video 不接收文件参数"""
        import inspect
        sig = inspect.signature(resize_video)
        
        assert 'input_files' not in sig.parameters
        assert 'width' in sig.parameters
        assert 'height' in sig.parameters
        assert 'scale' in sig.parameters

    def test_extract_frames_no_file_params(self):
        """确保 extract_frames 不接收文件参数"""
        import inspect
        sig = inspect.signature(extract_frames)
        
        assert 'input_files' not in sig.parameters
        assert 'times' in sig.parameters
        assert 'image_format' in sig.parameters


class TestReturnValues:
    """测试返回值（v3.0 架构）"""

    def test_returns_no_file_paths(self):
        """确保返回值不包含文件路径字段"""
        # 测试无输入的情况
        result = video_to_audio()
        
        # v3.0: 返回值不应包含文件路径
        assert "output_file" not in result
        assert "output_files" not in result
        assert "input_file" not in result
        assert "input_files" not in result
        
        # 应该包含业务字段
        assert "success" in result
        assert "error_code" in result  # 因为失败了
