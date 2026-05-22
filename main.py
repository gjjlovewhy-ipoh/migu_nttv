import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# 目标地址
LIVE_URL = "https://m.miguvideo.com/m/liveDetail/955227985?channelId=10010001005"
OUTPUT_FILE = "iptv_source.txt"
CHANNEL_NAME = "南通新闻综合"

# 过滤重复与无效链接
def filter_source(url_list):
    valid = []
    seen = set()
    rule = re.compile(r"https.+?\.m3u8")
    for url in url_list:
        res = rule.findall(url)
        for item in res:
            if item not in seen and "miguvideo" in item:
                seen.add(item)
                valid.append(item)
    return valid

def get_migu_live_source():
    source_list = []
    with sync_playwright() as p:
        # 启动浏览器，无头模式
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()

        # 监听网络请求，拦截直播地址
        def handle_request(req):
            req_url = req.url
            if ".m3u8" in req_url:
                source_list.append(req_url)

        page.on("request", handle_request)
        page.goto(LIVE_URL, timeout=30000)
        # 等待视频加载
        page.wait_for_timeout(8000)
        browser.close()
    
    return filter_source(source_list)

def save_txt(sources):
    content = "iptv,#genre#\n"
    for src in sources:
        content += f"{CHANNEL_NAME},{src}\n"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"抓取完成，获取到{len(sources)}条有效直播源")
    print(content)

if __name__ == "__main__":
    live_sources = get_migu_live_source()
    save_txt(live_sources)
