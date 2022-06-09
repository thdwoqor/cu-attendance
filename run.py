import json
import os
import time
from datetime import datetime
from urllib.request import Request, urlopen

import requests
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from util.driver import driver

load_dotenv(verbose=True)


def login():
    address = get_address()

    driver.get(f"https://www.pocketcu.co.kr/login?referer_url=https%3A%2F%2Fwww.pocketcu.co.kr%2Fevent%2FeventView%2F{address}")

    time.sleep(10)

    print(driver.current_url)

    id = driver.find_element(By.CSS_SELECTOR, "#loginId")
    id.send_keys(os.getenv("ID"))

    pw = driver.find_element(By.CSS_SELECTOR, "#loginPwd")
    pw.send_keys(os.getenv("PW"))

    element = driver.find_element(By.CSS_SELECTOR, "#loginForm > div > div.btn_wrap > a")
    driver.execute_script("arguments[0].click();", element)

    time.sleep(10)

    print(driver.current_url)


def get_address() -> str:
    try:
        page = requests.post(f"https://pocketcu.co.kr/api/v1/event?page=1&pagePerSize=999&evtStatus=ing&cateId=all", timeout=10)

        if page.status_code != 200:
            raise
        doc = page.text

    except:
        req = Request(f"https://pocketcu.co.kr/api/v1/event?page=1&pagePerSize=999&evtStatus=ing&cateId=all")
        page = urlopen(req, timeout=10)
        doc = page.read().decode("utf-8")
    finally:
        dict = json.loads(doc)
        keywords = ["출석룰렛", "출석 룰렛"]

        for i in dict["eventList"]:
            if any(keyword in i["prdDispNm"] for keyword in keywords):
                return i["evtCd"]


def attendance():
    time.sleep(10)

    now_count = driver.find_element(By.CSS_SELECTOR, "#myAttendCnt").text
    now_total = driver.find_element(By.CSS_SELECTOR, "#myAttendPoint").text
    print(now_count, now_total)

    element = driver.find_element(
        By.CSS_SELECTOR, "#contents > section > section > section.sub_wrap > div.event_area > div > div > div > div.roulette_main > div > div"
    )
    driver.execute_script("arguments[0].click();", element)

    time.sleep(10)

    driver.refresh()

    time.sleep(10)

    count = driver.find_element(By.CSS_SELECTOR, "#myAttendCnt").text
    total = driver.find_element(By.CSS_SELECTOR, "#myAttendPoint").text
    point = int(total) - int(now_total)
    print(count, total, point)

    if now_count != count:
        edit_readme(count, total, point)
        edit_record(point)


def edit_readme(count: str, total: str, point: int):
    file_path = "README.md"

    with open(file_path, "r", encoding="UTF8") as f:
        text = f.readlines()
        index = text.index(">포켓 CU 출석체크 봇\n") + 4
        text[index] = f" {count} | {total} | {point}\n"

    with open(file_path, "w", encoding="UTF8") as f:
        for e in text:
            f.write(e)


def edit_record(point: int):
    today = dict()
    today["point"] = point
    today["when"] = str(datetime.today())

    with open("record.json", "r", encoding="UTF8") as f:
        data = json.load(f)
    with open("record.json", "w", encoding="UTF8") as f:
        data.append(today)
        json.dump(data, f, indent="\t")


if __name__ == "__main__":
    login()
    attendance()
    driver.quit()
