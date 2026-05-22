import requests
import re
import json
from datetime import datetime
from urllib.parse import urlparse

# 基础配置
LIVE_DETAIL_URL = "https://m.miguvideo.com/m/liveDetail/955227985?channelId=10010001005"
CHANNEL_ID = "10010001005"
LIVE_ID = "955227985"
OUTPUT_FILE = "iptv_source.txt"
CHANNEL_NAME = "南通新闻综合"

# 通用请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Referer": "https://m.miguvideo.com/"
}

def get_live_info():
    """获取直播基础信息与播放密钥"""
    session = requests.Session()
    try:
        # 先访问详情页获取cookie与基础参数
        session.get(LIVE_DETAIL_URL, headers=HEADERS, timeout=20)
        
        # 咪咕直播播放接口
        api_url = f"https://m.miguvideo.com/miguvideo/live/getLivePlayInfo"
        params = {
            "liveId": LIVE_ID,
            "channelId": CHANNEL_ID,
            "vType": "3",
            "terminalType": "2"
        }
        res = session.get(api_url, params=params, headers=HEADERS, timeout=20)
        res_data = res.json()
        return res_data
    except Exception as e:
        print(f"接口请求失败：{e}")
        return None

def parse_m3u8_source(api_data):
    """解析接口返回数据，提取有效播放源"""
    source_list = []
    if not api_data or api_data.get("code") != 200:
        return source_list
    
    play_info = api_data.get("data", {})
    stream_list = play_info.get("streamList", [])
    
    for stream in stream_list:
        play_url = stream.get("playUrl")
        if play_url and ".m3u8" in play_url:
            source_list.append(play_url)
    
    # 去重
    unique_sources = list(set(source_list))
    return unique_sources

def save_iptv_file(source_list):
    """按指定格式保存文本"""
    lines = ["iptv,#genre#"]
    for src in source_list:
        lines.append(f"{CHANNEL_NAME},{src}")
    
    content = "\n".join(lines)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[{datetime.now()}] 抓取完成，共获取 {len(source_list)} 条直播源")
    print(content)

if __name__ == "__main__":
    info_data = get_live_info()
    sources = parse_m3u8_source(info_data)
    save_iptv_file(sources)
