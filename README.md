# 火山引擎视频生成 MCP 服务器

基于火山引擎 Seedance 系列模型的视频生成 MCP (Model Context Protocol) 服务器,支持文生视频、图生视频等多种视频生成能力。

## 功能特性

- ✅ 支持所有 Seedance 系列模型 (1.0/1.5 pro, pro-fast, lite)
- ✅ 文生视频 (Text-to-Video)
- ✅ 图生视频 (Image-to-Video)
  - 首帧图生视频
  - 首尾帧图生视频
  - 参考图生视频 (1-4张)
- ✅ Draft 模式 (快速预览,仅 Seedance 1.5 pro)
- ✅ 音频生成控制 (仅 Seedance 1.5 pro)
- ✅ 异步任务轮询
- ✅ 完整的参数控制 (分辨率、宽高比、时长、种子等)

## 安装

### 1. 克隆或下载项目

```bash
cd huoshan_mcp
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

复制 `.env.example` 为 `.env` 并填入您的火山引擎 API Key:

```bash
cp .env.example .env
```

编辑 `.env` 文件:

```
VOLCES_API_KEY=your_actual_api_key_here
```

获取 API Key: [火山引擎控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)

### 4. 配置 MCP 客户端

将 `mcp-config-example.json` 的内容添加到您的 MCP 客户端配置中 (如 Claude Desktop 的配置文件)。

**注意**: 修改 `cwd` 路径为您的实际项目路径,并设置正确的 `VOLCES_API_KEY`。

## 使用方法

### 工具列表

#### 1. `create_video_task` - 创建视频生成任务

创建一个视频生成任务并返回任务 ID,需要后续调用 `query_video_task` 查询状态。

**适用场景**: 批量创建任务、异步处理

**基本参数**:
- `model` (必填): 模型 ID
  - `doubao-seedance-1-5-pro-251215` - 最新版本,支持音频生成
  - `doubao-seedance-1-0-pro` - 标准版本
  - `doubao-seedance-1-0-pro-fast` - 快速版本
  - `doubao-seedance-1-0-lite-t2v` - 轻量版文生视频
  - `doubao-seedance-1-0-lite-i2v` - 轻量版图生视频

**内容参数**:
- `prompt` (可选): 文本提示词,描述期望生成的视频内容
- `images` (可选): 图片列表,用于图生视频
  - `url`: 图片 URL 或 Base64 编码
  - `role`: 图片角色 (`first_frame`/`last_frame`/`reference_image`)
- `draft_task_id` (可选): Draft 视频任务 ID,用于生成正式视频

**视频参数**:
- `resolution`: 分辨率 (`480p`/`720p`/`1080p`)
- `ratio`: 宽高比 (`16:9`/`4:3`/`1:1`/`3:4`/`9:16`/`21:9`/`adaptive`)
- `duration`: 视频时长(秒),2-12 秒
- `seed`: 随机种子,-1 表示随机
- `camera_fixed`: 是否固定摄像头
- `watermark`: 是否包含水印

**Seedance 1.5 pro 特有参数**:
- `generate_audio`: 是否生成音频,默认 true
- `draft`: 是否开启 Draft 模式,默认 false

**其他参数**:
- `return_last_frame`: 是否返回尾帧图像
- `service_tier`: 服务等级 (`default`/`flex`)
- `execution_expires_after`: 任务超时时间(秒)

**示例**:

```json
{
  "model": "doubao-seedance-1-5-pro-251215",
  "prompt": "一只可爱的小猫在草地上玩耍,阳光明媚,3D卡通风格",
  "resolution": "720p",
  "ratio": "16:9",
  "duration": 5,
  "generate_audio": true
}
```

#### 2. `generate_video` - 生成视频(自动轮询)

创建视频生成任务并自动轮询直到完成,直接返回视频 URL。

**适用场景**: 需要立即获取结果的场景

**参数**: 与 `create_video_task` 相同,额外支持:
- `max_wait_time`: 最大等待时间(秒),默认 600 (10分钟)
- `poll_interval`: 轮询间隔(秒),默认 5

**示例**:

```json
{
  "model": "doubao-seedance-1-5-pro-251215",
  "prompt": "夕阳下的海滩,海浪轻轻拍打着沙滩,电影级画质",
  "resolution": "1080p",
  "ratio": "16:9",
  "duration": 8,
  "max_wait_time": 600,
  "poll_interval": 5
}
```

#### 3. `query_video_task` - 查询任务状态

查询视频生成任务的状态和结果。

**参数**:
- `task_id` (必填): 任务 ID

**返回状态**:
- `queued`: 排队中
- `running`: 运行中
- `succeeded`: 成功 (包含 `video_url`)
- `failed`: 失败 (包含 `error` 信息)
- `expired`: 超时
- `cancelled`: 已取消

**示例**:

```json
{
  "task_id": "cgt-20250123123456-abcde"
}
```

### 使用示例

#### 示例 1: 文生视频

```
请使用火山引擎生成一段视频:
- 内容: 一只橘猫在窗台上晒太阳,慵懒地打哈欠
- 模型: doubao-seedance-1-5-pro-251215
- 分辨率: 720p
- 时长: 5秒
- 需要音频
```

#### 示例 2: 图生视频 (首帧)

```
使用这张图片生成视频:
- 图片URL: https://example.com/cat.jpg
- 提示词: 小猫开始奔跑,追逐蝴蝶
- 模型: doubao-seedance-1-0-pro
- 分辨率: 1080p
```

#### 示例 3: 图生视频 (首尾帧)

```
使用首尾帧生成视频:
- 首帧: https://example.com/start.jpg
- 尾帧: https://example.com/end.jpg
- 提示词: 平滑过渡,自然运动
- 模型: doubao-seedance-1-5-pro-251215
```

#### 示例 4: Draft 模式

```
先生成 Draft 视频预览:
1. 创建 Draft 任务 (draft=true, resolution=480p)
2. 查看 Draft 视频效果
3. 如果满意,使用 draft_task_id 生成正式视频
```

## 模型对比

| 模型 | 文生视频 | 图生视频(首帧) | 图生视频(首尾帧) | 参考图 | 音频 | Draft |
|------|---------|---------------|----------------|--------|------|-------|
| Seedance 1.5 pro | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Seedance 1.0 pro | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Seedance 1.0 pro-fast | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Seedance 1.0 lite t2v | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Seedance 1.0 lite i2v | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |

## 注意事项

1. **API Key 安全**: 请妥善保管您的 API Key,不要提交到版本控制系统
2. **任务有效期**: 生成的视频和任务记录仅保存 7 天,请及时下载
3. **视频有效期**: 生成的视频 URL 有效期为 24 小时,请及时转存
4. **计费相关**:
   - Draft 模式消耗 token 更少,适合快速验证
   - `service_tier=flex` 价格为在线推理的 50%
   - 视频时长影响计费,请合理设置
5. **图片要求**:
   - 格式: jpeg, png, webp, bmp, tiff, gif (1.5 pro 额外支持 heic, heif)
   - 宽高比: 0.4 - 2.5
   - 尺寸: 300-6000 像素
   - 大小: < 30 MB

## 错误处理

服务器会返回详细的错误信息,常见错误:

- `API key is required`: 未设置 API Key
- `Failed to create task`: 任务创建失败,检查参数是否正确
- `Task failed`: 任务执行失败,查看 error 字段获取详细信息
- `Task timeout`: 任务超时,可能需要增加 `max_wait_time`

## 开发

### 项目结构

```
huoshan_mcp/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── server.py            # MCP 服务器主文件
│   ├── volces_client.py     # 火山引擎 API 客户端
│   └── models.py            # 数据模型定义
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
├── README.md               # 本文档
└── mcp-config-example.json # MCP 配置示例
```

### 运行服务器

```bash
python -m src.server
```

## 相关链接

- [火山引擎方舟平台](https://console.volcengine.com/ark)
- [API 文档](https://www.volcengine.com/docs/82379/1520758)
- [模型列表](https://www.volcengine.com/docs/82379/1330310)
- [提示词指南](https://www.volcengine.com/docs/82379/1587797)
- [MCP 协议](https://modelcontextprotocol.io/)

## 许可证

MIT License

## 更新日志

### v1.0.0 (2026-01-23)

- 初始版本
- 支持所有 Seedance 系列模型
- 支持文生视频、图生视频
- 支持 Draft 模式和音频生成
- 提供自动轮询和手动查询两种模式
