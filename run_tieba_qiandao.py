import os
import json
import time
from DrissionPage import ChromiumPage, ChromiumOptions

print("程序开始运行")

# 从环境变量读取 cookies
cookies_str = os.environ.get("TIEBA_COOKIES")

if not cookies_str:
    print("未检测到 cookies，退出")
    exit(1)

cookies = json.loads(cookies_str)

print("正在启动浏览器...")

# 浏览器配置
co = ChromiumOptions()

# GitHub Actions 必须加这些参数
co.set_argument('--no-sandbox')
co.set_argument('--disable-dev-shm-usage')
co.set_argument('--disable-gpu')
co.set_argument('--headless=new')

page = ChromiumPage(co)

print("浏览器启动成功")

# 打开贴吧
page.get("https://tieba.baidu.com")

print("正在注入 cookies...")

# 添加 cookies
for cookie in cookies:
    try:
        page.set.cookies(cookie)
    except:
        pass

# 刷新页面
page.refresh()

time.sleep(3)

print("开始签到...")

# 进入贴吧首页
page.get("https://tieba.baidu.com/index.html")

time.sleep(5)

# 点击一键签到
try:
    page.ele("text=一键签到").click()
    print("点击一键签到成功")
except:
    print("未找到一键签到按钮")

time.sleep(5)

print("签到完成")
