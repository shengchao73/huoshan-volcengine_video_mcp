"""
数据模型定义
"""
from typing import Optional, List, Literal, Union
from dataclasses import dataclass


@dataclass
class ImageContent:
    """图片内容"""
    url: str
    role: Optional[Literal["first_frame", "last_frame", "reference_image"]] = None


@dataclass
class VideoTaskRequest:
    """视频生成任务请求"""
    model: str
    prompt: Optional[str] = None
    images: Optional[List[ImageContent]] = None
    draft_task_id: Optional[str] = None

    # 视频参数
    resolution: Optional[Literal["480p", "720p", "1080p"]] = None
    ratio: Optional[Literal["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"]] = None
    duration: Optional[int] = None
    frames: Optional[int] = None
    seed: Optional[int] = None
    camera_fixed: Optional[bool] = None
    watermark: Optional[bool] = None

    # Seedance 1.5 pro 特有参数
    generate_audio: Optional[bool] = None
    draft: Optional[bool] = None

    # 其他参数
    callback_url: Optional[str] = None
    return_last_frame: Optional[bool] = None
    service_tier: Optional[Literal["default", "flex"]] = None
    execution_expires_after: Optional[int] = None


@dataclass
class VideoTaskStatus:
    """视频任务状态"""
    id: str
    model: str
    status: Literal["queued", "running", "cancelled", "succeeded", "failed", "expired"]
    created_at: int
    updated_at: int
    video_url: Optional[str] = None
    last_frame_url: Optional[str] = None
    error: Optional[dict] = None
    seed: Optional[int] = None
    resolution: Optional[str] = None
    ratio: Optional[str] = None
    duration: Optional[int] = None
    frames: Optional[int] = None
    framespersecond: Optional[int] = None
    generate_audio: Optional[bool] = None
    draft: Optional[bool] = None
    draft_task_id: Optional[str] = None
    service_tier: Optional[str] = None
    execution_expires_after: Optional[int] = None
    usage: Optional[dict] = None
