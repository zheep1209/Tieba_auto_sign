import os
# 防止 DrissionPage 自动下载浏览器导致卡死
os.environ["DP_NO_BROWSER_DOWNLOAD"] = "1"

from DrissionPage import ChromiumOptions, ChromiumPage
import json
import time
import requests


def read_cookie():
    """读取 cookie，优先从环境变量读取"""
    if "TIEBA_COOKIES" in os.environ:
        return json.loads(os.environ["TIEBA_COOKIES"])
    else:
        print("贴吧Cookie未配置！详细请参考教程！")
        return []


def get_level_exp(page):
    """获取等级和经验，如果找不到返回'未知'"""
    try:
        level_ele = page.ele(
            'xpath://*[@id="pagelet_aside/pagelet/my_tieba"]/div/div[1]/div[3]/div[1]/a/div[2]'
        ).text
        level = level_ele if level_ele else "未知"
    except:
        level = "未知"

    try:
        exp_ele = page.ele(
            'xpath://*[@id="pagelet_aside/pagelet/my_tieba"]/div/div[1]/div[3]/div[2]/a/div[2]/span[1]'
        ).text
        exp = exp_ele if exp_ele else "未知"
    except:
        exp = "未知"

    return level, exp


if __name__ == "__main__":
    print("程序开始运行")

    # 通知信息
    notice = ""

    print("正在启动浏览器...")

    co = ChromiumOptions()
    co.headless(True)
    co.disable_gpu(True)
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--disable-blink-features=AutomationControlled')

    page = ChromiumPage(co)

    print("浏览器启动成功")

    url = "https://tieba.baidu.com/"
    page.get(url, timeout=30)

    cookies = read_cookie()
    if cookies:
        page.set.cookies(cookies)

    page.refresh()
    page._wait_loaded(15)

    print("开始签到流程")

    over = False
    yeshu = 0
    count = 0

    while not over:
        yeshu += 1
        print(f"正在处理第 {yeshu} 页")

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
                msg = f"全部爬取完成！本次总共签到 {count} 个吧..."
                print(msg)
                notice += msg + "\n\n"
                page.close()
                over = True
                break

            print(f"进入 {name} 吧")

            page.get(tieba_url, timeout=30)

            page.wait.eles_loaded(
                'xpath://*[@id="signstar_wrapper"]/a/span[1]',
                timeout=30
            )

            # 判断是否签到
            is_sign_ele = page.ele(
                'xpath://*[@id="signstar_wrapper"]/a/span[1]'
            )
            is_sign = is_sign_ele.text if is_sign_ele else ""

            if is_sign.startswith("连续"):
                level, exp = get_level_exp(page)
                msg = f"{name}吧：已签到过！等级：{level}，经验：{exp}"
                print(msg)
                notice += msg + "\n\n"
                print("-------------------------------------------------")

            else:
                page.wait.eles_loaded(
                    'xpath://a[@class="j_signbtn sign_btn_bright j_cansign"]',
                    timeout=30
                )

                sign_ele = page.ele(
                    'xpath://a[@class="j_signbtn sign_btn_bright j_cansign"]'
                )

                if sign_ele:
                    sign_ele.click()
                    time.sleep(1)

                    sign_ele.click()
                    time.sleep(1)

                    page.refresh()
                    page._wait_loaded(15)

                    level, exp = get_level_exp(page)
                    msg = f"{name}吧：成功！等级：{level}，经验：{exp}"
                    print(msg)
                    notice += msg + "\n\n"
                    print("-------------------------------------------------")

                else:
                    msg = f"错误！{name}吧：找不到签到按钮"
                    print(msg)
                    notice += msg + "\n\n"
                    print("-------------------------------------------------")

            count += 1

            page.back()
            page._wait_loaded(10)

    print("签到完成")

    # Server酱推送
    if "SendKey" in os.environ:
        api = f'https://sc.ftqq.com/{os.environ["SendKey"]}.send'
        title = "贴吧签到信息"

        data = {
            "text": title,
            "desp": notice
        }

        try:
            req = requests.post(api, data=data, timeout=60)

            if req.status_code == 200:
                print("Server酱通知发送成功")
            else:
                print(f"通知失败，状态码：{req.status_code}")

        except Exception as e:
            print(f"通知发送异常：{e}")

    else:
        print("未配置Server酱服务...")
