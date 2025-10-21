"""
main.py 的单元测试

测试所有视频处理函数的功能
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import (
    video_to_audio,
    concatenate_videos,
    trim_video,
    resize_video,
    extract_audio_segment,
    get_video_info
)


class TestVideoToAudio:
    """测试 video_to_audio 函数"""

    def test_file_not_found(self):
        """测试文件不存在的情况"""
        result = video_to_audio("nonexistent.mp4")
        assert result["success"] is False
        assert result["error_code"] == "FILE_NOT_FOUND"
        assert "不存在" in result["error"]

    @patch('src.main.VideoFileClip')
    def test_no_audio_track(self, mock_video_clip):
        """测试视频无音频轨道的情况"""
        # 创建临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            # Mock VideoFileClip
            mock_instance = Mock()
            mock_instance.audio = None  # 模拟无音频轨道
            mock_video_clip.return_value = mock_instance

            result = video_to_audio(temp_path)

            assert result["success"] is False
            assert result["error_code"] == "NO_AUDIO_TRACK"
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @patch('src.main.VideoFileClip')
    def test_successful_conversion(self, mock_video_clip):
        """测试成功转换"""
        # 创建临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            # Mock VideoFileClip 和 audio
            mock_audio = Mock()
            mock_audio.write_audiofile = Mock()

            mock_instance = Mock()
            mock_instance.audio = mock_audio
            mock_instance.duration = 120.5
            mock_instance.close = Mock()

            mock_video_clip.return_value = mock_instance

            result = video_to_audio(temp_path, audio_format="mp3")

            assert result["success"] is True
            assert "output_file" in result
            assert result["format"] == "mp3"
            assert result["duration"] == 120.5
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            # 清理可能生成的输出文件
            output_file = result.get("output_file")
            if output_file and os.path.exists(output_file):
                os.remove(output_file)


class TestConcatenateVideos:
    """测试 concatenate_videos 函数"""

    def test_insufficient_videos(self):
        """测试视频数量不足"""
        result = concatenate_videos([])
        assert result["success"] is False
        assert result["error_code"] == "INSUFFICIENT_VIDEOS"

        result = concatenate_videos(["single.mp4"])
        assert result["success"] is False
        assert result["error_code"] == "INSUFFICIENT_VIDEOS"

    def test_file_not_found(self):
        """测试文件不存在"""
        result = concatenate_videos(["file1.mp4", "file2.mp4"])
        assert result["success"] is False
        assert result["error_code"] == "FILE_NOT_FOUND"


class TestTrimVideo:
    """测试 trim_video 函数"""

    def test_file_not_found(self):
        """测试文件不存在"""
        result = trim_video("nonexistent.mp4", 0, 10)
        assert result["success"] is False
        assert result["error_code"] == "FILE_NOT_FOUND"

    def test_invalid_start_time(self):
        """测试无效的开始时间"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            result = trim_video(temp_path, -5, 10)
            assert result["success"] is False
            assert result["error_code"] == "INVALID_START_TIME"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_invalid_time_range(self):
        """测试无效的时间范围"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            result = trim_video(temp_path, 10, 5)
            assert result["success"] is False
            assert result["error_code"] == "INVALID_TIME_RANGE"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @patch('src.main.VideoFileClip')
    def test_time_out_of_range(self, mock_video_clip):
        """测试时间超出视频长度"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            # Mock VideoFileClip
            mock_instance = Mock()
            mock_instance.duration = 100.0
            mock_instance.close = Mock()
            mock_video_clip.return_value = mock_instance

            result = trim_video(temp_path, 0, 150)

            assert result["success"] is False
            assert result["error_code"] == "TIME_OUT_OF_RANGE"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestResizeVideo:
    """测试 resize_video 函数"""

    def test_file_not_found(self):
        """测试文件不存在"""
        result = resize_video("nonexistent.mp4", width=1280)
        assert result["success"] is False
        assert result["error_code"] == "FILE_NOT_FOUND"

    def test_missing_size_parameter(self):
        """测试缺少尺寸参数"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            result = resize_video(temp_path)
            assert result["success"] is False
            assert result["error_code"] == "MISSING_SIZE_PARAMETER"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestExtractAudioSegment:
    """测试 extract_audio_segment 函数"""

    def test_file_not_found(self):
        """测试文件不存在"""
        result = extract_audio_segment("nonexistent.mp3", 0, 10)
        assert result["success"] is False
        assert result["error_code"] == "FILE_NOT_FOUND"

    def test_invalid_start_time(self):
        """测试无效的开始时间"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        try:
            result = extract_audio_segment(temp_path, -5, 10)
            assert result["success"] is False
            assert result["error_code"] == "INVALID_START_TIME"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_invalid_time_range(self):
        """测试无效的时间范围"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        try:
            result = extract_audio_segment(temp_path, 10, 5)
            assert result["success"] is False
            assert result["error_code"] == "INVALID_TIME_RANGE"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestGetVideoInfo:
    """测试 get_video_info 函数"""

    def test_file_not_found(self):
        """测试文件不存在"""
        result = get_video_info("nonexistent.mp4")
        assert result["success"] is False
        assert result["error_code"] == "FILE_NOT_FOUND"

    @patch('src.main.VideoFileClip')
    def test_successful_info_retrieval(self, mock_video_clip):
        """测试成功获取视频信息"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            # 写入一些数据以便文件有大小
            f.write(b"dummy video data")
            temp_path = f.name

        try:
            # Mock VideoFileClip
            mock_instance = Mock()
            mock_instance.duration = 120.5
            mock_instance.fps = 30
            mock_instance.w = 1920
            mock_instance.h = 1080
            mock_instance.audio = Mock()  # 有音频
            mock_instance.close = Mock()
            mock_video_clip.return_value = mock_instance

            result = get_video_info(temp_path)

            assert result["success"] is True
            assert "info" in result
            assert result["info"]["duration"] == 120.5
            assert result["info"]["fps"] == 30
            assert result["info"]["width"] == 1920
            assert result["info"]["height"] == 1080
            assert result["info"]["has_audio"] is True
            assert "file_size_bytes" in result["info"]
            assert "file_size_mb" in result["info"]
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestParameterValidation:
    """测试参数验证"""

    def test_video_to_audio_formats(self):
        """测试不同的音频格式参数"""
        result = video_to_audio("nonexistent.mp4", audio_format="wav")
        assert result["success"] is False  # 因为文件不存在，但参数有效

        result = video_to_audio("nonexistent.mp4", audio_format="aac")
        assert result["success"] is False

    def test_resize_with_different_params(self):
        """测试不同的调整大小参数"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            # 测试只指定宽度
            result = resize_video(temp_path, width=1280)
            assert result["error_code"] != "MISSING_SIZE_PARAMETER"

            # 测试只指定高度
            result = resize_video(temp_path, height=720)
            assert result["error_code"] != "MISSING_SIZE_PARAMETER"

            # 测试只指定缩放比例
            result = resize_video(temp_path, scale=0.5)
            assert result["error_code"] != "MISSING_SIZE_PARAMETER"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
