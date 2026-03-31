from DrissionPage import ChromiumOptions, ChromiumPage
import json
import os
import shutil
import time
import requests


def read_cookie():
    """读取 cookie"""
    if "TIEBA_COOKIES" in os.environ:
        try:
            return json.loads(os.environ["TIEBA_COOKIES"])
        except:
            print("Cookie解析失败")
            return []
    else:
        print("未配置贴吧Cookie")
        return []


if __name__ == "__main__":

    print("程序开始运行")

    notice = ""

    print("正在启动浏览器...")

    co = ChromiumOptions()

    co.headless(True)
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-dev-shm-usage")
    co.set_argument("--disable-gpu")

    chromium_path = shutil.which("chromium-browser")
    if chromium_path:
        co.set_browser_path(chromium_path)

    page = ChromiumPage(co)

    print("浏览器启动成功")

    page.get("https://tieba.baidu.com")

    print("正在注入 cookies...")

    cookies = read_cookie()
    if cookies:
        page.set.cookies(cookies)

    page.refresh()

    time.sleep(5)

    print("开始签到...")

    yeshu = 1
    count = 0
    over = False

    while not over:

        print(f"正在处理第 {yeshu} 页")

        page.get(f"https://tieba.baidu.com/i/i/forum?&pn={yeshu}")

        time.sleep(5)

        for i in range(1, 30):

            try:
                tieba = page.eles('css:.forum_table a')[i]
            except:
                over = True
                break

            try:
                name = tieba.text
                url = tieba.link
            except:
                continue

            print(f"进入 {name} 吧")

            try:
                page.get(url)
            except:
                continue

            time.sleep(3)

            try:

                btn = page.ele("text=签到")

                if btn:
                    btn.click()
                    print(f"{name} 签到成功")
                    notice += f"{name} 签到成功\n"
                else:
                    print(f"{name} 已签到")
                    notice += f"{name} 已签到\n"

            except:
                print(f"{name} 签到失败")
                notice += f"{name} 签到失败\n"

            count += 1

            page.back()

            time.sleep(2)

        yeshu += 1

    print("签到完成")

    print("准备发送通知")

    sendkey = os.environ.get("SendKey")

    if sendkey:

        api = f"https://sctapi.ftqq.com/{sendkey}.send"

        data = {
            "title": "贴吧签到完成",
            "desp": notice
        }

        try:

            resp = requests.post(api, data=data)

            print("通知发送成功")

        except Exception as e:

            print("通知发送失败", e)

    else:

        print("未配置Server酱")
