#!/usr/bin/env python3
"""
火山引擎视频生成 MCP 服务器
提供视频生成任务创建、查询和自动轮询功能
"""
import os
import json
import asyncio
from typing import Any, Optional
from dotenv import load_dotenv

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from .volces_client import VolcesVideoClient
from .models import VideoTaskRequest, ImageContent

# 加载环境变量
load_dotenv()

# 创建服务器实例
server = Server("huoshan-video-server")

# 全局客户端实例
client: Optional[VolcesVideoClient] = None


def get_client() -> VolcesVideoClient:
    """获取或创建客户端实例"""
    global client
    if client is None:
        client = VolcesVideoClient()
    return client


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出所有可用工具"""
    return [
        types.Tool(
            name="create_video_task",
            description=(
                "创建火山引擎视频生成任务并返回任务ID。"
                "支持文生视频、图生视频(首帧/首尾帧/参考图)、Draft模式等。"
                "创建后需要使用query_video_task查询任务状态。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": (
                            "模型ID,推荐选择：doubao-seedance-1-0-pro-fast-251015可选值:\n"
                            "doubao-seedance-1-5-pro-251215 (最新,支持音频)\n"
                            "doubao-seedance-1-0-pro-250528\n"
                            "doubao-seedance-1-0-pro-fast-251015\n"
                            "doubao-seedance-1-0-lite-t2v-250428 (文生视频)\n"
                            "doubao-seedance-1-0-lite-i2v-250428 (图生视频)"
                        )
                    },
                    "prompt": {
                        "type": "string",
                        "description": "文本提示词,描述期望生成的视频内容。建议不超过500字。"
                    },
                    "images": {
                        "type": "array",
                        "description": "图片列表,用于图生视频。每个图片包含url和可选的role字段。",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "图片URL或Base64编码(格式: data:image/png;base64,...)"
                                },
                                "role": {
                                    "type": "string",
                                    "enum": ["first_frame", "last_frame", "reference_image"],
                                    "description": "图片角色: first_frame(首帧), last_frame(尾帧), reference_image(参考图)"
                                }
                            },
                            "required": ["url"]
                        }
                    },
                    "draft_task_id": {
                        "type": "string",
                        "description": "Draft视频任务ID,用于基于Draft生成正式视频(仅Seedance 1.5 pro)"
                    },
                    "resolution": {
                        "type": "string",
                        "enum": ["480p", "720p", "1080p"],
                        "description": "视频分辨率,默认720p(1.5 pro/1.0 lite)或1080p(1.0 pro)"
                    },
                    "ratio": {
                        "type": "string",
                        "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"],
                        "description": "视频宽高比,adaptive表示自动选择"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "视频时长(秒),支持2-12秒。Seedance 1.5 pro支持-1(自动选择4-12秒)"
                    },
                    "frames": {
                        "type": "integer",
                        "description": "视频帧数,与duration二选一。支持[29,289]区间内满足25+4n的整数"
                    },
                    "seed": {
                        "type": "integer",
                        "description": "随机种子,用于控制生成内容的随机性。-1表示随机"
                    },
                    "camera_fixed": {
                        "type": "boolean",
                        "description": "是否固定摄像头,默认false"
                    },
                    "watermark": {
                        "type": "boolean",
                        "description": "是否包含水印,默认false"
                    },
                    "generate_audio": {
                        "type": "boolean",
                        "description": "是否生成音频(仅Seedance 1.5 pro),默认true"
                    },
                    "draft": {
                        "type": "boolean",
                        "description": "是否开启Draft模式(仅Seedance 1.5 pro),默认false"
                    },
                    "return_last_frame": {
                        "type": "boolean",
                        "description": "是否返回尾帧图像,默认false"
                    },
                    "service_tier": {
                        "type": "string",
                        "enum": ["default", "flex"],
                        "description": "服务等级: default(在线推理)或flex(离线推理,价格50%)"
                    },
                    "execution_expires_after": {
                        "type": "integer",
                        "description": "任务超时时间(秒),默认172800(48小时),范围[3600,259200]"
                    }
                },
                "required": ["model"]
            }
        ),
        types.Tool(
            name="generate_video",
            description=(
                "创建视频生成任务并自动轮询直到完成。"
                "适合需要立即获取结果的场景。"
                "参数与create_video_task相同,额外支持max_wait_time和poll_interval。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": (
                            "模型ID,默认请选择：doubao-seedance-1-0-pro-fast-251015，可选值:\n"
                            "doubao-seedance-1-5-pro-251215 (最新,支持音频)\n"
                            "doubao-seedance-1-0-pro-250528\n"
                            "doubao-seedance-1-0-pro-fast-251015\n"
                            "doubao-seedance-1-0-lite-t2v-250428 (文生视频)\n"
                            "doubao-seedance-1-0-lite-i2v-250428 (图生视频)")
                    },
                    "prompt": {
                        "type": "string",
                        "description": "文本提示词"
                    },
                    "images": {
                        "type": "array",
                        "description": "图片列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"},
                                "role": {
                                    "type": "string",
                                    "enum": ["first_frame", "last_frame", "reference_image"]
                                }
                            },
                            "required": ["url"]
                        }
                    },
                    "draft_task_id": {"type": "string"},
                    "resolution": {
                        "type": "string",
                        "enum": ["480p", "720p", "1080p"]
                    },
                    "ratio": {
                        "type": "string",
                        "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"]
                    },
                    "duration": {"type": "integer"},
                    "frames": {"type": "integer"},
                    "seed": {"type": "integer"},
                    "camera_fixed": {"type": "boolean"},
                    "watermark": {"type": "boolean"},
                    "generate_audio": {"type": "boolean"},
                    "draft": {"type": "boolean"},
                    "return_last_frame": {"type": "boolean"},
                    "service_tier": {
                        "type": "string",
                        "enum": ["default", "flex"]
                    },
                    "execution_expires_after": {"type": "integer"},
                    "max_wait_time": {
                        "type": "integer",
                        "description": "最大等待时间(秒),默认600秒(10分钟)"
                    },
                    "poll_interval": {
                        "type": "integer",
                        "description": "轮询间隔(秒),默认5秒"
                    }
                },
                "required": ["model"]
            }
        ),
        types.Tool(
            name="query_video_task",
            description="查询视频生成任务的状态和结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务ID"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用"""
    if not arguments:
        arguments = {}

    try:
        client = get_client()

        if name == "create_video_task":
            # 解析参数
            images = None
            if "images" in arguments:
                images = [
                    ImageContent(
                        url=img["url"],
                        role=img.get("role")
                    )
                    for img in arguments["images"]
                ]

            request = VideoTaskRequest(
                model=arguments["model"],
                prompt=arguments.get("prompt"),
                images=images,
                draft_task_id=arguments.get("draft_task_id"),
                resolution=arguments.get("resolution"),
                ratio=arguments.get("ratio"),
                duration=arguments.get("duration"),
                frames=arguments.get("frames"),
                seed=arguments.get("seed"),
                camera_fixed=arguments.get("camera_fixed"),
                watermark=arguments.get("watermark"),
                generate_audio=arguments.get("generate_audio"),
                draft=arguments.get("draft"),
                callback_url=arguments.get("callback_url"),
                return_last_frame=arguments.get("return_last_frame"),
                service_tier=arguments.get("service_tier"),
                execution_expires_after=arguments.get("execution_expires_after")
            )

            task_id = await client.create_task(request)

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "task_id": task_id,
                        "message": "视频生成任务已创建,请使用query_video_task查询任务状态"
                    }, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "generate_video":
            # 解析参数
            images = None
            if "images" in arguments:
                images = [
                    ImageContent(
                        url=img["url"],
                        role=img.get("role")
                    )
                    for img in arguments["images"]
                ]

            request = VideoTaskRequest(
                model=arguments["model"],
                prompt=arguments.get("prompt"),
                images=images,
                draft_task_id=arguments.get("draft_task_id"),
                resolution=arguments.get("resolution"),
                ratio=arguments.get("ratio"),
                duration=arguments.get("duration"),
                frames=arguments.get("frames"),
                seed=arguments.get("seed"),
                camera_fixed=arguments.get("camera_fixed"),
                watermark=arguments.get("watermark"),
                generate_audio=arguments.get("generate_audio"),
                draft=arguments.get("draft"),
                callback_url=arguments.get("callback_url"),
                return_last_frame=arguments.get("return_last_frame"),
                service_tier=arguments.get("service_tier"),
                execution_expires_after=arguments.get("execution_expires_after")
            )

            # 创建任务
            task_id = await client.create_task(request)

            # 轮询任务
            max_wait_time = arguments.get("max_wait_time", 600)
            poll_interval = arguments.get("poll_interval", 5)

            status = await client.poll_task(task_id, max_wait_time, poll_interval)

            # 构建响应
            result = {
                "success": True,
                "task_id": status.id,
                "status": status.status,
                "video_url": status.video_url,
                "model": status.model,
                "created_at": status.created_at,
                "updated_at": status.updated_at
            }

            # 添加可选字段
            if status.last_frame_url:
                result["last_frame_url"] = status.last_frame_url
            if status.seed is not None:
                result["seed"] = status.seed
            if status.resolution:
                result["resolution"] = status.resolution
            if status.ratio:
                result["ratio"] = status.ratio
            if status.duration is not None:
                result["duration"] = status.duration
            if status.frames is not None:
                result["frames"] = status.frames
            if status.framespersecond is not None:
                result["framespersecond"] = status.framespersecond
            if status.generate_audio is not None:
                result["generate_audio"] = status.generate_audio
            if status.draft is not None:
                result["draft"] = status.draft
            if status.draft_task_id:
                result["draft_task_id"] = status.draft_task_id
            if status.usage:
                result["usage"] = status.usage

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "query_video_task":
            task_id = arguments["task_id"]
            status = await client.query_task(task_id)

            # 构建响应
            result = {
                "task_id": status.id,
                "status": status.status,
                "model": status.model,
                "created_at": status.created_at,
                "updated_at": status.updated_at
            }

            # 添加视频URL(如果已完成)
            if status.video_url:
                result["video_url"] = status.video_url
            if status.last_frame_url:
                result["last_frame_url"] = status.last_frame_url

            # 添加错误信息(如果失败)
            if status.error:
                result["error"] = status.error

            # 添加其他字段
            if status.seed is not None:
                result["seed"] = status.seed
            if status.resolution:
                result["resolution"] = status.resolution
            if status.ratio:
                result["ratio"] = status.ratio
            if status.duration is not None:
                result["duration"] = status.duration
            if status.frames is not None:
                result["frames"] = status.frames
            if status.framespersecond is not None:
                result["framespersecond"] = status.framespersecond
            if status.generate_audio is not None:
                result["generate_audio"] = status.generate_audio
            if status.draft is not None:
                result["draft"] = status.draft
            if status.draft_task_id:
                result["draft_task_id"] = status.draft_task_id
            if status.service_tier:
                result["service_tier"] = status.service_tier
            if status.execution_expires_after is not None:
                result["execution_expires_after"] = status.execution_expires_after
            if status.usage:
                result["usage"] = status.usage

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e)
                }, ensure_ascii=False, indent=2)
            )
        ]


async def main():
    """主函数"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="huoshan-video-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
