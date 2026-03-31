import os
os.environ["DP_NO_BROWSER_DOWNLOAD"] = "1"

from DrissionPage import ChromiumOptions, ChromiumPage
import json
import time
import requests


def read_cookie():
    """读取 cookie"""
    if "TIEBA_COOKIES" in os.environ:
        return json.loads(os.environ["TIEBA_COOKIES"])
    else:
        print("贴吧Cookie未配置")
        return []


def get_level_exp(page):
    """获取等级经验"""
    try:
        level = page.ele(
            'xpath://*[@id="pagelet_aside/pagelet/my_tieba"]/div/div[1]/div[3]/div[1]/a/div[2]'
        ).text
    except:
        level = "未知"

    try:
        exp = page.ele(
            'xpath://*[@id="pagelet_aside/pagelet/my_tieba"]/div/div[1]/div[3]/div[2]/a/div[2]/span[1]'
        ).text
    except:
        exp = "未知"

    return level, exp


if __name__ == "__main__":
    print("程序开始运行")

    notice = ""

    print("正在启动浏览器...")

    co = ChromiumOptions()
    co.headless(True)

    # GitHub Actions 必备参数
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-dev-shm-usage")
    co.set_argument("--disable-gpu")
    co.set_argument("--disable-blink-features=AutomationControlled")

    page = ChromiumPage(co)

    print("浏览器启动成功")

    page.get("https://tieba.baidu.com/", timeout=30)

    cookies = read_cookie()
    if cookies:
        page.set.cookies(cookies)

    page.refresh()
    page._wait_loaded(15)

    print("开始签到")

    over = False
    yeshu = 0
    count = 0

    while not over:
        yeshu += 1
        print(f"第 {yeshu} 页")

        page.get(
            f"https://tieba.baidu.com/i/i/forum?&pn={yeshu}",
            timeout=30
        )

        page._wait_loaded(15)

        for i in range(2, 22):

            element = page.ele(
                f'xpath://*[@id="like_pagelet"]/div[1]/div[1]/table/tbody/tr[{i}]/td[1]/a'
            )

            try:
                tieba_url = element.attr("href")
                name = element.attr("title")
            except:
                print(f"完成，共签到 {count}")
                page.close()
                over = True
                break

            print(f"进入 {name}")

            page.get(tieba_url, timeout=30)

            page.wait.eles_loaded(
                'xpath://*[@id="signstar_wrapper"]/a/span[1]',
                timeout=30
            )

            is_sign_ele = page.ele(
                'xpath://*[@id="signstar_wrapper"]/a/span[1]'
            )

            is_sign = is_sign_ele.text if is_sign_ele else ""

            if is_sign.startswith("连续"):
                level, exp = get_level_exp(page)
                print(f"{name} 已签到 等级:{level} 经验:{exp}")

            else:
                sign_ele = page.ele(
                    'xpath://a[@class="j_signbtn sign_btn_bright j_cansign"]'
                )

                if sign_ele:
                    sign_ele.click()
                    time.sleep(1)
                    sign_ele.click()

                    print(f"{name} 签到成功")

                else:
                    print(f"{name} 找不到签到按钮")

            count += 1

            page.back()
            page._wait_loaded(10)

    print("签到完成")

    if "SendKey" in os.environ:
        api = f'https://sc.ftqq.com/{os.environ["SendKey"]}.send'

        requests.post(
            api,
            data={
                "text": "贴吧签到",
                "desp": notice
            },
            timeout=60
        )
