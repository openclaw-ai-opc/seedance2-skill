#!/usr/bin/env python3
"""
Seedance 2.0 视频生成脚本

功能：
- 提交视频生成任务
- 自动轮询任务状态
- 下载生成的视频

使用示例：
python generate_video.py --token YOUR_TOKEN --prompt "写实风格，蓝天白云下的花田"
"""

import argparse
import json
import time
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Any


class SeedanceVideoGenerator:
    """Seedance 2.0 视频生成器"""
    
    BASE_URL = "https://dzwlai.com/apiuser/_open/ai/task/api"
    
    def __init__(self, token: str):
        self.token = token
    
    def submit_task(
        self,
        prompt: str,
        model_name: str = "seedance-2-0-fast",
        duration: int = 5,
        resolution: str = "480p",
        aspect_ratio: str = "16:9",
        generate_audio: bool = False,
        watermark: bool = False,
        web_search: bool = False,
        return_last_frame: bool = True,
        callback_url: str = ""
    ) -> Dict[str, Any]:
        """提交视频生成任务"""
        
        url = f"{self.BASE_URL}/seedance/gene2video"
        
        payload = {
            "modelName": model_name,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "generate_audio": generate_audio,
            "watermark": watermark,
            "web_search": web_search,
            "return_last_frame": return_last_frame,
            "callbackUrl": callback_url
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-token": self.token
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return {"code": e.code, "msg": f"HTTP Error: {error_body}"}
        except Exception as e:
            return {"code": -1, "msg": f"Error: {str(e)}"}
    
    def get_task_state(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        
        url = f"{self.BASE_URL}/getState?ids={task_id}"
        
        headers = {
            "x-token": self.token
        }
        
        req = urllib.request.Request(url, headers=headers, method='GET')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return {"code": e.code, "msg": f"HTTP Error: {error_body}"}
        except Exception as e:
            return {"code": -1, "msg": f"Error: {str(e)}"}
    
    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 5,
        max_wait: int = 600,
        verbose: bool = True
    ) -> Optional[Dict[str, Any]]:
        """等待任务完成"""
        
        elapsed = 0
        
        while elapsed < max_wait:
            result = self.get_task_state(task_id)
            
            if result.get("code") != 200:
                if verbose:
                    print(f"❌ 查询失败: {result.get('msg')}")
                return None
            
            data = result.get("data", {})
            if isinstance(data, list) and len(data) > 0:
                task_info = data[0]
            else:
                task_info = data
            
            status = task_info.get("status", "unknown")
            
            if verbose:
                print(f"⏳ 任务状态: {status} (已等待 {elapsed}秒)")
            
            if status == "success":
                if verbose:
                    print("✅ 视频生成成功!")
                return task_info
            elif status == "failed":
                if verbose:
                    print(f"❌ 视频生成失败: {task_info.get('error', '未知错误')}")
                return None
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        if verbose:
            print(f"⏰ 超时: 等待超过 {max_wait} 秒")
        return None
    
    def download_video(self, video_url: str, output_path: str) -> bool:
        """下载视频文件"""
        
        try:
            urllib.request.urlretrieve(video_url, output_path)
            print(f"✅ 视频已保存到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 下载失败: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Seedance 2.0 视频生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python generate_video.py --token YOUR_TOKEN --prompt "写实风格，蓝天下的花田"
  python generate_video.py --token YOUR_TOKEN --prompt "动漫风格，少女在樱花树下" --duration 10 --resolution 720p
        """
    )
    
    parser.add_argument("--token", required=True, help="API令牌")
    parser.add_argument("--prompt", required=True, help="视频描述提示词")
    parser.add_argument("--model", default="seedance-2-0-fast", help="模型名称")
    parser.add_argument("--duration", type=int, default=5, help="视频时长（秒）")
    parser.add_argument("--resolution", default="480p", help="分辨率")
    parser.add_argument("--aspect-ratio", default="16:9", help="宽高比")
    parser.add_argument("--generate-audio", action="store_true", help="生成音频")
    parser.add_argument("--no-watermark", action="store_true", help="去除水印")
    parser.add_argument("--web-search", action="store_true", help="启用网络搜索")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--poll-interval", type=int, default=5, help="轮询间隔（秒）")
    parser.add_argument("--max-wait", type=int, default=600, help="最大等待时间（秒）")
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = SeedanceVideoGenerator(args.token)
    
    # 提交任务
    print(f"🚀 提交视频生成任务...")
    print(f"   提示词: {args.prompt}")
    print(f"   时长: {args.duration}秒")
    print(f"   分辨率: {args.resolution}")
    print(f"   宽高比: {args.aspect_ratio}")
    
    result = generator.submit_task(
        prompt=args.prompt,
        model_name=args.model,
        duration=args.duration,
        resolution=args.resolution,
        aspect_ratio=args.aspect_ratio,
        generate_audio=args.generate_audio,
        watermark=not args.no_watermark,
        web_search=args.web_search
    )
    
    if result.get("code") != 200:
        print(f"❌ 提交失败: {result.get('msg')}")
        sys.exit(1)
    
    task_data = result.get("data", {})
    task_id = task_data.get("id")
    
    print(f"✅ 任务已提交")
    print(f"   任务ID: {task_id}")
    print(f"   {result.get('msg')}")
    
    # 等待完成
    print(f"\n⏳ 等待视频生成...")
    task_info = generator.wait_for_completion(
        task_id,
        poll_interval=args.poll_interval,
        max_wait=args.max_wait
    )
    
    if not task_info:
        sys.exit(1)
    
    # 输出结果
    video_url = task_info.get("videoUrl") or task_info.get("video_url")
    
    if video_url:
        print(f"\n🎬 视频URL: {video_url}")
        
        # 下载视频
        if args.output:
            generator.download_video(video_url, args.output)
    else:
        print(f"\n📋 任务信息: {json.dumps(task_info, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
