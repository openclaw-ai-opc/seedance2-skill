---
name: seedance2-skill
description: Seedance 2.0 AI视频生成技能。通过DZWL AI API根据文本提示词生成视频。触发场景：用户要求"生成视频"、"AI视频"、"文生视频"、"视频创作"、"seedance"等。支持自然语言描述生成视频，自动轮询任务状态直到视频生成完成并返回视频URL。
---

# Seedance Video - AI视频生成

## 概述

本技能封装了 DZWL AI 的 Seedance 2.0 视频生成 API，支持通过自然语言描述生成高质量视频。

**核心能力：**
- 文本生成视频（Text-to-Video）
- 支持多种分辨率（480p、720p等）
- 支持多种宽高比（16:9、9:16、1:1等）
- 可选音频生成
- 自动轮询任务状态直到完成

## 使用流程

### 1. 发起视频生成任务

调用 API 提交生成任务，获取任务 ID：

```bash
curl --request POST \
  --url https://dzwlai.com/apiuser/_open/ai/task/api/seedance/gene2video \
  --header 'Content-Type: application/json' \
  --header 'x-token: <YOUR_TOKEN>' \
  --data '{
    "modelName": "seedance-2-0-fast",
    "prompt": "写实风格，晴朗的蓝天之下，一大片白色的雏菊花田，镜头逐渐拉近，最终定格在一朵雏菊花的特写上，花瓣上有几颗晶莹的露珠",
    "duration": 5,
    "resolution": "480p",
    "aspect_ratio": "16:9",
    "generate_audio": true,
    "watermark": false,
    "web_search": false,
    "return_last_frame": true,
    "callbackUrl": ""
  }'
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "您已成功提交创作任务，目前剩余并发任务数为3",
  "data": {
    "id": "1909553892857782274",
    "status": "create"
  }
}
```

### 2. 查询任务状态

使用任务 ID 轮询获取生成结果：

```bash
curl --request GET \
  --url 'https://dzwlai.com/apiuser/_open/ai/task/api/getState?ids=<TASK_ID>' \
  --header 'x-token: <YOUR_TOKEN>'
```

**任务状态：**
- `create` - 任务已创建
- `processing` - 正在生成
- `success` - 生成成功（返回视频URL）
- `failed` - 生成失败

### 3. 获取视频结果

当状态为 `success` 时，响应中会包含视频下载 URL。

## 参数说明

### 必填参数

| 参数 | 类型 | 说明 |
|------|------|------|
| modelName | string | 模型名称，固定为 `seedance-2-0-fast` |
| prompt | string | 视频描述提示词，支持中英文 |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| duration | number | 5 | 视频时长（秒） |
| resolution | string | "480p" | 分辨率：480p、720p等 |
| aspect_ratio | string | "16:9" | 宽高比：16:9、9:16、1:1等 |
| generate_audio | boolean | false | 是否生成音频 |
| watermark | boolean | true | 是否添加水印 |
| web_search | boolean | false | 是否启用网络搜索增强 |
| return_last_frame | boolean | false | 是否返回最后一帧 |
| callbackUrl | string | "" | 回调URL（可选） |

## 最佳实践

### 提示词编写建议

1. **明确风格**：开头说明风格（写实、动漫、电影感等）
2. **场景描述**：清晰描述场景、主体、动作
3. **镜头运动**：描述镜头变化（拉近、推远、平移等）
4. **细节补充**：添加光影、氛围等细节

**示例提示词：**
```
写实风格，晴朗的蓝天之下，一大片白色的雏菊花田，
镜头逐渐拉近，最终定格在一朵雏菊花的特写上，
花瓣上有几颗晶莹的露珠
```

### 分辨率选择建议

- **480p**：快速预览，生成速度快
- **720p**：平衡质量与速度
- **1080p**：高质量输出（如支持）

### 宽高比选择

- **16:9**：横屏视频，适合风景、电影
- **9:16**：竖屏视频，适合短视频平台
- **1:1**：方形视频，适合社交媒体

## 脚本工具

本技能提供了 Python 脚本简化 API 调用：

### scripts/generate_video.py

自动化视频生成脚本，封装了任务提交和状态轮询。

```bash
python scripts/generate_video.py \
  --token <YOUR_TOKEN> \
  --prompt "你的视频描述" \
  --duration 5 \
  --resolution 480p \
  --aspect-ratio 16:9 \
  --generate-audio
```

**参数：**
- `--token`：API令牌（必填）
- `--prompt`：视频描述（必填）
- `--duration`：时长（秒）
- `--resolution`：分辨率
- `--aspect-ratio`：宽高比
- `--generate-audio`：生成音频标志
- `--no-watermark`：去除水印
- `--output`：输出文件路径

## 错误处理

### 常见错误

1. **令牌无效**：检查 x-token 是否正确
2. **并发限制**：等待其他任务完成
3. **参数错误**：检查请求参数格式

### 重试策略

- 网络错误：指数退避重试
- 并发限制：等待后重试
- 生成失败：检查提示词是否合规

## API 参考

详细 API 文档见：[references/api_reference.md](references/api_reference.md)
