import requests
import re
import json
from datetime import datetime

# 目标直播页面地址
LIVE_URL = "https://m.miguvideo.com/m/liveDetail/955227985?channelId=10010001005"
# 输出文件
OUTPUT_FILE = "iptv_source.txt"
# 频道名称
CHANNEL_NAME = "南通新闻综合"

# 请求头伪装浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://m.miguvideo.com/"
}

def get_live_source():
    live_urls = []
    try:
        resp = requests.get(LIVE_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # 正则匹配m3u8直播源
        m3u8_pattern = re.compile(r'https?://.*?\.m3u8[^"\']]*')
        m3u8_list = m3u8_pattern.findall(html)
        
        # 去重过滤无效地址
        unique_src = list(set(m3u8_list))
        for src in unique_src:
            if len(src) > 30 and "miguvideo" in src:
                live_urls.append(src)
                
    except Exception as e:
        print(f"抓取异常：{str(e)}")
    return live_urls

def save_iptv_txt(source_list):
    # 固定头部格式
    content = "iptv,#genre#\n"
    for url in source_list:
        content += f"{CHANNEL_NAME},{url}\n"
    
    # 写入文本
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[{datetime.now()}] 源地址已保存完成，共{len(source_list)}条直播源")
    print(content)

if __name__ == "__main__":
    sources = get_live_source()
    save_iptv_txt(sources)
