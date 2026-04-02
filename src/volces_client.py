"""
火山引擎视频生成API客户端
"""
import os
import asyncio
from typing import Optional, List, Dict, Any
import httpx
from .models import VideoTaskRequest, VideoTaskStatus, ImageContent


class VolcesVideoClient:
    """火山引擎视频生成API客户端"""

    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: API密钥,如果不提供则从环境变量VOLCES_API_KEY读取
        """
        self.api_key = api_key or os.getenv("VOLCES_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set VOLCES_API_KEY environment variable or pass api_key parameter.")

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

    async def create_task(self, request: VideoTaskRequest) -> str:
        """
        创建视频生成任务

        Args:
            request: 视频任务请求

        Returns:
            任务ID

        Raises:
            httpx.HTTPError: HTTP请求失败
            ValueError: API返回错误
        """
        # 构建请求体
        payload: Dict[str, Any] = {
            "model": request.model
        }

        # 构建content数组
        content = []

        # 添加文本内容
        if request.prompt:
            content.append({
                "type": "text",
                "text": request.prompt
            })

        # 添加图片内容
        if request.images:
            for img in request.images:
                img_obj = {
                    "type": "image_url",
                    "image_url": {
                        "url": img.url
                    }
                }
                if img.role:
                    img_obj["role"] = img.role
                content.append(img_obj)

        # 添加draft_task内容
        if request.draft_task_id:
            content.append({
                "type": "draft_task",
                "draft_task": {
                    "id": request.draft_task_id
                }
            })

        if content:
            payload["content"] = content

        # 添加可选参数
        optional_params = {
            "resolution": request.resolution,
            "ratio": request.ratio,
            "duration": request.duration,
            "frames": request.frames,
            "seed": request.seed,
            "camera_fixed": request.camera_fixed,
            "watermark": request.watermark,
            "generate_audio": request.generate_audio,
            "draft": request.draft,
            "callback_url": request.callback_url,
            "return_last_frame": request.return_last_frame,
            "service_tier": request.service_tier,
            "execution_expires_after": request.execution_expires_after
        }

        for key, value in optional_params.items():
            if value is not None:
                payload[key] = value

        # 发送请求
        response = await self.client.post(
            f"{self.BASE_URL}/contents/generations/tasks",
            json=payload
        )

        response.raise_for_status()
        result = response.json()

        # 提取任务ID
        if "id" in result:
            return result["id"]
        else:
            raise ValueError(f"Failed to create task: {result}")

    async def query_task(self, task_id: str) -> VideoTaskStatus:
        """
        查询视频生成任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态

        Raises:
            httpx.HTTPError: HTTP请求失败
        """
        response = await self.client.get(
            f"{self.BASE_URL}/contents/generations/tasks/{task_id}"
        )

        response.raise_for_status()
        result = response.json()

        # 解析响应
        status = VideoTaskStatus(
            id=result.get("id", task_id),
            model=result.get("model", ""),
            status=result.get("status", "unknown"),
            created_at=result.get("created_at", 0),
            updated_at=result.get("updated_at", 0),
            error=result.get("error")
        )

        # 提取content中的video_url和last_frame_url
        if "content" in result and result["content"]:
            content = result["content"]
            status.video_url = content.get("video_url")
            status.last_frame_url = content.get("last_frame_url")

        # 提取其他字段
        status.seed = result.get("seed")
        status.resolution = result.get("resolution")
        status.ratio = result.get("ratio")
        status.duration = result.get("duration")
        status.frames = result.get("frames")
        status.framespersecond = result.get("framespersecond")
        status.generate_audio = result.get("generate_audio")
        status.draft = result.get("draft")
        status.draft_task_id = result.get("draft_task_id")
        status.service_tier = result.get("service_tier")
        status.execution_expires_after = result.get("execution_expires_after")
        status.usage = result.get("usage")

        return status

    async def poll_task(
        self,
        task_id: str,
        max_wait_time: int = 600,
        poll_interval: int = 5
    ) -> VideoTaskStatus:
        """
        轮询任务直到完成或超时

        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间(秒),默认600秒(10分钟)
            poll_interval: 轮询间隔(秒),默认5秒

        Returns:
            任务状态

        Raises:
            TimeoutError: 超时
            ValueError: 任务失败
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            status = await self.query_task(task_id)

            # 检查任务状态
            if status.status == "succeeded":
                return status
            elif status.status in ["failed", "expired", "cancelled"]:
                error_msg = status.error.get("message", "Unknown error") if status.error else "Task failed"
                raise ValueError(f"Task {status.status}: {error_msg}")

            # 检查超时
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= max_wait_time:
                raise TimeoutError(f"Task polling timeout after {max_wait_time} seconds. Current status: {status.status}")

            # 等待后继续轮询
            await asyncio.sleep(poll_interval)

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
