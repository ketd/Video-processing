"""
集成测试 - 使用真实视频文件

这个测试套件使用真实的测试视频 tests/啥是大语言模型.mp4 进行完整的功能测试。
按照项目最佳实践，使用真实数据进行测试以确保功能的正确性和可重现性。
"""

import sys
import os
import pytest

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


class TestRealVideoProcessing:
    """使用真实视频文件的集成测试"""

    @pytest.fixture
    def test_video_path(self):
        """提供真实的测试视频文件路径"""
        return os.path.join(os.path.dirname(__file__), "啥是大语言模型.mp4")

    @pytest.fixture
    def cleanup_files(self):
        """测试后清理生成的文件"""
        created_files = []
        yield created_files
        # 测试结束后清理
        for file_path in created_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"✓ 已清理: {file_path}")
                except Exception as e:
                    print(f"✗ 清理失败 {file_path}: {e}")

    def test_get_video_info_real(self, test_video_path):
        """测试获取真实视频信息"""
        result = get_video_info(test_video_path)

        assert result["success"] is True, f"获取视频信息失败: {result.get('error')}"

        info = result["info"]
        print(f"\n视频信息:")
        print(f"  时长: {info['duration']:.2f} 秒")
        print(f"  分辨率: {info['width']}x{info['height']}")
        print(f"  帧率: {info['fps']} FPS")
        print(f"  文件大小: {info['file_size_mb']} MB")
        print(f"  有音频: {'是' if info['has_audio'] else '否'}")

        # 验证视频属性
        assert info["duration"] > 0, "视频时长应大于 0"
        assert info["width"] == 1280, "视频宽度应为 1280"
        assert info["height"] == 720, "视频高度应为 720"
        assert info["fps"] == 30.0, "帧率应为 30 FPS"
        assert info["has_audio"] is True, "视频应该包含音频"
        assert info["file_size_mb"] > 0, "文件大小应大于 0"

    def test_video_to_audio_real(self, test_video_path, cleanup_files):
        """测试将真实视频转换为音频"""
        output_path = "test_output_audio.mp3"
        cleanup_files.append(output_path)

        result = video_to_audio(
            video_path=test_video_path,
            output_path=output_path,
            audio_format="mp3",
            audio_bitrate="192k"
        )

        print(f"\n视频转音频结果:")
        print(f"  成功: {result['success']}")
        if result["success"]:
            print(f"  输出文件: {result['output_file']}")
            print(f"  音频格式: {result['format']}")
            print(f"  时长: {result['duration']:.2f} 秒")

        assert result["success"] is True, f"转换失败: {result.get('error')}"
        assert os.path.exists(result["output_file"]), "输出文件应该存在"
        assert result["format"] == "mp3", "格式应为 mp3"
        assert result["duration"] > 0, "音频时长应大于 0"

        # 检查输出文件大小
        file_size = os.path.getsize(result["output_file"])
        print(f"  输出文件大小: {file_size / (1024*1024):.2f} MB")
        assert file_size > 0, "输出文件应该有内容"

    def test_video_to_audio_wav(self, test_video_path, cleanup_files):
        """测试转换为 WAV 格式"""
        output_path = "test_output_audio.wav"
        cleanup_files.append(output_path)

        result = video_to_audio(
            video_path=test_video_path,
            output_path=output_path,
            audio_format="wav"
        )

        assert result["success"] is True, f"转换失败: {result.get('error')}"
        assert os.path.exists(result["output_file"]), "输出文件应该存在"
        assert result["format"] == "wav", "格式应为 wav"

    def test_trim_video_real(self, test_video_path, cleanup_files):
        """测试剪辑真实视频（提取前 10 秒）"""
        output_path = "test_trimmed_video.mp4"
        cleanup_files.append(output_path)

        result = trim_video(
            video_path=test_video_path,
            start_time=0,
            end_time=10,
            output_path=output_path
        )

        print(f"\n视频剪辑结果:")
        print(f"  成功: {result['success']}")
        if result["success"]:
            print(f"  输出文件: {result['output_file']}")
            print(f"  剪辑时长: {result['duration']:.2f} 秒")
            print(f"  开始时间: {result['start_time']} 秒")
            print(f"  结束时间: {result['end_time']} 秒")

        assert result["success"] is True, f"剪辑失败: {result.get('error')}"
        assert os.path.exists(result["output_file"]), "输出文件应该存在"
        assert abs(result["duration"] - 10.0) < 0.1, "剪辑时长应该约为 10 秒"

        # 检查输出文件大小
        file_size = os.path.getsize(result["output_file"])
        print(f"  输出文件大小: {file_size / (1024*1024):.2f} MB")
        assert file_size > 0, "输出文件应该有内容"

    def test_trim_video_middle_segment(self, test_video_path, cleanup_files):
        """测试剪辑视频中间片段"""
        output_path = "test_middle_segment.mp4"
        cleanup_files.append(output_path)

        result = trim_video(
            video_path=test_video_path,
            start_time=30,
            end_time=40,
            output_path=output_path
        )

        assert result["success"] is True, f"剪辑失败: {result.get('error')}"
        assert abs(result["duration"] - 10.0) < 0.1, "剪辑时长应该约为 10 秒"

    def test_resize_video_by_width(self, test_video_path, cleanup_files):
        """测试按宽度调整视频大小（保持宽高比）"""
        output_path = "test_resized_640.mp4"
        cleanup_files.append(output_path)

        result = resize_video(
            video_path=test_video_path,
            width=640,
            output_path=output_path
        )

        print(f"\n视频调整大小结果:")
        print(f"  成功: {result['success']}")
        if result["success"]:
            print(f"  输出文件: {result['output_file']}")
            print(f"  原始尺寸: {result['original_size']['width']}x{result['original_size']['height']}")
            print(f"  新尺寸: {result['new_size']['width']}x{result['new_size']['height']}")

        assert result["success"] is True, f"调整大小失败: {result.get('error')}"
        assert os.path.exists(result["output_file"]), "输出文件应该存在"
        assert result["original_size"]["width"] == 1280, "原始宽度应为 1280"
        assert result["original_size"]["height"] == 720, "原始高度应为 720"
        assert result["new_size"]["width"] == 640, "新宽度应为 640"
        assert result["new_size"]["height"] == 360, "新高度应为 360（保持宽高比）"

        # 检查文件大小减小
        original_size = os.path.getsize(test_video_path)
        new_size = os.path.getsize(result["output_file"])
        print(f"  原始文件: {original_size / (1024*1024):.2f} MB")
        print(f"  新文件: {new_size / (1024*1024):.2f} MB")
        print(f"  压缩率: {(1 - new_size/original_size)*100:.1f}%")

    def test_resize_video_by_scale(self, test_video_path, cleanup_files):
        """测试按比例缩放视频"""
        output_path = "test_resized_half.mp4"
        cleanup_files.append(output_path)

        result = resize_video(
            video_path=test_video_path,
            scale=0.5,
            output_path=output_path
        )

        assert result["success"] is True, f"调整大小失败: {result.get('error')}"
        assert result["new_size"]["width"] == 640, "缩放后宽度应为 640"
        assert result["new_size"]["height"] == 360, "缩放后高度应为 360"

    def test_resize_video_by_height(self, test_video_path, cleanup_files):
        """测试按高度调整视频大小"""
        output_path = "test_resized_480.mp4"
        cleanup_files.append(output_path)

        result = resize_video(
            video_path=test_video_path,
            height=480,
            output_path=output_path
        )

        assert result["success"] is True, f"调整大小失败: {result.get('error')}"
        assert result["new_size"]["height"] == 480, "新高度应为 480"
        # 宽度应该按比例调整：1280 * (480/720) ≈ 853
        assert abs(result["new_size"]["width"] - 853) < 2, "宽度应该按比例调整"

    def test_extract_audio_then_segment(self, test_video_path, cleanup_files):
        """测试组合操作：先提取音频，再提取音频片段"""
        # 第一步：提取音频
        audio_path = "test_full_audio.mp3"
        cleanup_files.append(audio_path)

        result1 = video_to_audio(
            video_path=test_video_path,
            output_path=audio_path
        )
        assert result1["success"] is True, "提取音频失败"

        # 第二步：提取音频片段
        segment_path = "test_audio_segment.mp3"
        cleanup_files.append(segment_path)

        result2 = extract_audio_segment(
            audio_path=audio_path,
            start_time=10,
            end_time=20,
            output_path=segment_path
        )

        print(f"\n组合操作结果:")
        print(f"  提取音频: {result1['success']}")
        print(f"  提取片段: {result2['success']}")
        if result2["success"]:
            print(f"  片段时长: {result2['duration']:.2f} 秒")

        assert result2["success"] is True, f"提取音频片段失败: {result2.get('error')}"
        assert os.path.exists(segment_path), "音频片段文件应该存在"
        assert abs(result2["duration"] - 10.0) < 0.1, "片段时长应该约为 10 秒"

    def test_workflow_trim_then_resize(self, test_video_path, cleanup_files):
        """测试工作流：先剪辑再调整大小"""
        # 第一步：剪辑视频（取前 30 秒）
        trimmed_path = "test_workflow_trimmed.mp4"
        cleanup_files.append(trimmed_path)

        result1 = trim_video(
            video_path=test_video_path,
            start_time=0,
            end_time=30,
            output_path=trimmed_path
        )
        assert result1["success"] is True, "剪辑失败"

        # 第二步：调整大小
        final_path = "test_workflow_final.mp4"
        cleanup_files.append(final_path)

        result2 = resize_video(
            video_path=trimmed_path,
            width=854,
            height=480,
            output_path=final_path
        )

        print(f"\n工作流测试结果:")
        print(f"  步骤 1 - 剪辑: {result1['success']}")
        print(f"  步骤 2 - 调整大小: {result2['success']}")
        if result2["success"]:
            original_size = os.path.getsize(test_video_path)
            final_size = os.path.getsize(final_path)
            print(f"  原始文件: {original_size / (1024*1024):.2f} MB")
            print(f"  最终文件: {final_size / (1024*1024):.2f} MB")
            print(f"  总压缩率: {(1 - final_size/original_size)*100:.1f}%")

        assert result2["success"] is True, "调整大小失败"
        assert os.path.exists(final_path), "最终文件应该存在"

    def test_multiple_formats_conversion(self, test_video_path, cleanup_files):
        """测试转换为多种音频格式"""
        formats = ["mp3", "wav", "aac"]

        for fmt in formats:
            output_path = f"test_audio.{fmt}"
            cleanup_files.append(output_path)

            result = video_to_audio(
                video_path=test_video_path,
                output_path=output_path,
                audio_format=fmt
            )

            print(f"\n转换为 {fmt.upper()}:")
            print(f"  成功: {result['success']}")
            if result["success"] and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"  文件大小: {file_size / (1024*1024):.2f} MB")

            assert result["success"] is True, f"转换为 {fmt} 失败: {result.get('error')}"
            assert os.path.exists(output_path), f"{fmt} 文件应该存在"


class TestEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def test_video_path(self):
        """提供真实的测试视频文件路径"""
        return os.path.join(os.path.dirname(__file__), "啥是大语言模型.mp4")

    def test_trim_at_video_end(self, test_video_path):
        """测试在视频末尾附近剪辑"""
        # 获取视频时长
        info_result = get_video_info(test_video_path)
        duration = info_result["info"]["duration"]

        # 尝试提取最后 5 秒
        result = trim_video(
            video_path=test_video_path,
            start_time=duration - 5,
            end_time=duration,
            output_path="test_end_trim.mp4"
        )

        try:
            assert result["success"] is True, "应该能够在视频末尾剪辑"
            assert abs(result["duration"] - 5.0) < 0.5, "时长应该约为 5 秒"
        finally:
            # 清理
            if result.get("output_file") and os.path.exists(result["output_file"]):
                os.remove(result["output_file"])

    def test_trim_beyond_duration(self, test_video_path):
        """测试超出视频长度的剪辑"""
        result = trim_video(
            video_path=test_video_path,
            start_time=0,
            end_time=999999,  # 远超视频长度
            output_path="test_invalid.mp4"
        )

        assert result["success"] is False, "应该返回失败"
        assert result["error_code"] == "TIME_OUT_OF_RANGE", "错误代码应为 TIME_OUT_OF_RANGE"

    def test_very_short_trim(self, test_video_path):
        """测试非常短的剪辑（0.5秒）"""
        output_path = "test_very_short.mp4"

        result = trim_video(
            video_path=test_video_path,
            start_time=0,
            end_time=0.5,
            output_path=output_path
        )

        try:
            assert result["success"] is True, "应该能够剪辑很短的片段"
            assert result["duration"] > 0, "时长应该大于 0"
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

