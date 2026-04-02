# 火山引擎视频生成 MCP 使用示例

## 示例 1: 简单文生视频

**用户提示**:
```
请使用火山引擎生成一段视频:一只可爱的橘猫在阳光下的草地上玩耍,追逐蝴蝶,3D卡通风格,5秒钟
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "一只可爱的橘猫在阳光下的草地上玩耍,追逐蝴蝶,3D卡通风格",
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 5,
    "generate_audio": true
  }
}
```

---

## 示例 2: 高质量文生视频(无音频)

**用户提示**:
```
生成一段电影级的日落海滩视频,1080p,8秒,不需要音频
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "夕阳西下,金色的阳光洒在海面上,海浪轻轻拍打着沙滩,远处有几只海鸥飞过,电影级画质,宁静祥和的氛围",
    "resolution": "1080p",
    "ratio": "16:9",
    "duration": 8,
    "generate_audio": false,
    "watermark": false
  }
}
```

---

## 示例 3: 图生视频(首帧)

**用户提示**:
```
使用这张图片生成视频: https://example.com/cat-sitting.jpg
让猫咪站起来,伸懒腰,然后开始走动
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-0-pro",
    "prompt": "猫咪慢慢站起来,优雅地伸了个懒腰,然后开始在房间里悠闲地走动",
    "images": [
      {
        "url": "https://example.com/cat-sitting.jpg",
        "role": "first_frame"
      }
    ],
    "resolution": "1080p",
    "ratio": "16:9",
    "duration": 6
  }
}
```

---

## 示例 4: 图生视频(首尾帧)

**用户提示**:
```
使用首尾帧生成视频:
- 首帧: https://example.com/flower-bud.jpg (花苞)
- 尾帧: https://example.com/flower-bloom.jpg (盛开的花)
生成花朵绽放的过程
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "花朵缓缓绽放,花瓣逐渐展开,展现生命的美丽瞬间",
    "images": [
      {
        "url": "https://example.com/flower-bud.jpg",
        "role": "first_frame"
      },
      {
        "url": "https://example.com/flower-bloom.jpg",
        "role": "last_frame"
      }
    ],
    "resolution": "720p",
    "ratio": "1:1",
    "duration": 5,
    "generate_audio": true
  }
}
```

---

## 示例 5: 参考图生视频

**用户提示**:
```
使用这些参考图生成视频:
- 图1: 男孩的照片
- 图2: 小狗的照片
- 图3: 公园的照片
生成男孩和小狗在公园玩耍的视频
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-0-lite-i2v",
    "prompt": "[图1]的男孩和[图2]的小狗在[图3]的公园里快乐地玩耍,男孩扔飞盘,小狗欢快地追逐",
    "images": [
      {
        "url": "https://example.com/boy.jpg",
        "role": "reference_image"
      },
      {
        "url": "https://example.com/dog.jpg",
        "role": "reference_image"
      },
      {
        "url": "https://example.com/park.jpg",
        "role": "reference_image"
      }
    ],
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 6
  }
}
```

---

## 示例 6: Draft 模式工作流

**步骤 1: 创建 Draft 视频**

**用户提示**:
```
先生成一个 Draft 预览视频,看看效果
内容: 科幻城市,飞行汽车穿梭其中
```

**工具调用**:
```json
{
  "tool": "create_video_task",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "未来科幻城市,高楼林立,霓虹灯闪烁,飞行汽车在空中穿梭,赛博朋克风格",
    "resolution": "480p",
    "ratio": "16:9",
    "duration": 5,
    "draft": true
  }
}
```

**返回**: `{"task_id": "cgt-draft-123456"}`

**步骤 2: 查询 Draft 状态**

```json
{
  "tool": "query_video_task",
  "arguments": {
    "task_id": "cgt-draft-123456"
  }
}
```

**步骤 3: 基于 Draft 生成正式视频**

**用户提示**:
```
Draft 效果不错,生成正式的高清版本
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "draft_task_id": "cgt-draft-123456",
    "resolution": "1080p",
    "generate_audio": true
  }
}
```

---

## 示例 7: 固定摄像头视频

**用户提示**:
```
生成一段固定机位的视频:咖啡杯里的咖啡冒着热气,背景是窗外的雨景
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "一杯热咖啡放在窗边的桌子上,咖啡冒着袅袅热气,窗外雨滴打在玻璃上,温馨宁静的氛围",
    "resolution": "1080p",
    "ratio": "16:9",
    "duration": 6,
    "camera_fixed": true,
    "generate_audio": true
  }
}
```

---

## 示例 8: 批量创建任务

**用户提示**:
```
批量创建3个视频任务:
1. 春天的樱花
2. 夏天的海滩
3. 秋天的枫叶
```

**工具调用 1**:
```json
{
  "tool": "create_video_task",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "春天,樱花盛开,粉色的花瓣随风飘落,阳光透过花瓣洒下斑驳的光影",
    "resolution": "720p",
    "duration": 5
  }
}
```

**工具调用 2**:
```json
{
  "tool": "create_video_task",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "夏天,蔚蓝的海滩,清澈的海水,白色的浪花拍打着沙滩,椰树随风摇曳",
    "resolution": "720p",
    "duration": 5
  }
}
```

**工具调用 3**:
```json
{
  "tool": "create_video_task",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "秋天,满山的枫叶红了,金黄和火红交织,秋风吹过,落叶纷飞",
    "resolution": "720p",
    "duration": 5
  }
}
```

然后使用 `query_video_task` 分别查询每个任务的状态。

---

## 示例 9: 使用特定种子复现视频

**用户提示**:
```
使用种子 12345 生成视频,这样可以复现相似的结果
```

**工具调用**:
```json
{
  "tool": "generate_video",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "魔法森林,发光的蘑菇,神秘的氛围,奇幻风格",
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 5,
    "seed": 12345
  }
}
```

---

## 示例 10: 离线推理模式(省钱)

**用户提示**:
```
使用离线推理模式生成视频,不着急要结果,可以省50%的费用
```

**工具调用**:
```json
{
  "tool": "create_video_task",
  "arguments": {
    "model": "doubao-seedance-1-5-pro-251215",
    "prompt": "宇宙深处,星云旋转,星星闪烁,壮丽的太空景象",
    "resolution": "1080p",
    "ratio": "16:9",
    "duration": 8,
    "service_tier": "flex",
    "execution_expires_after": 86400
  }
}
```

---

## 提示词技巧

### 1. 结构化描述
```
主体 + 动作 + 环境 + 风格 + 氛围
例: 一只白猫 + 在跳跃 + 在现代客厅里 + 3D卡通风格 + 温馨可爱
```

### 2. 使用具体细节
```
❌ 一只猫
✅ 一只毛茸茸的橘色小猫,有着明亮的绿色眼睛
```

### 3. 指定镜头和运动
```
- 镜头: 特写/中景/远景/俯视/仰视
- 运动: 缓慢推进/环绕/跟随/固定机位
```

### 4. 控制节奏
```
- 快节奏: 快速移动,动作迅速,节奏感强
- 慢节奏: 缓慢移动,优雅流畅,宁静祥和
```

### 5. 音频生成优化(Seedance 1.5 pro)
```
将对话放在双引号内:
男人转身对女人说:"今晚的月色真美。"
```

---

## 常见问题

### Q: 如何选择合适的模型?

- **Seedance 1.5 pro**: 最新最强,支持音频,推荐首选
- **Seedance 1.0 pro**: 标准版本,性能稳定
- **Seedance 1.0 pro-fast**: 快速生成,适合快速迭代
- **Seedance 1.0 lite**: 轻量版,成本更低

### Q: 视频生成需要多长时间?

- Draft 模式: 通常 1-3 分钟
- 正常模式: 通常 3-10 分钟
- 离线模式: 可能需要更长时间,但价格便宜 50%

### Q: 如何提高视频质量?

1. 使用详细的提示词
2. 选择更高的分辨率
3. 使用 Draft 模式先预览,满意后再生成正式版
4. 尝试不同的种子值
5. 对于图生视频,确保输入图片质量高

### Q: 视频 URL 有效期多久?

生成的视频 URL 有效期为 24 小时,请及时下载保存。

### Q: 如何节省成本?

1. 使用 Draft 模式预览
2. 使用 `service_tier=flex` 离线推理
3. 选择合适的分辨率和时长
4. 使用 lite 系列模型
