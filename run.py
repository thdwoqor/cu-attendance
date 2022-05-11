import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.driver import driver

load_dotenv(verbose=True)


def login():
    address = get_address()

    driver.get(f"https://www.pocketcu.co.kr/login?referer_url=https%3A%2F%2Fwww.pocketcu.co.kr%2Fevent%2FeventView%2F{address}")

    time.sleep(30)

    print(driver.current_url)

    id = driver.find_element(By.CSS_SELECTOR, "#loginId")
    id.send_keys(os.getenv("ID"))

    pw = driver.find_element(By.CSS_SELECTOR, "#loginPwd")
    pw.send_keys(os.getenv("PW"))

    element = driver.find_element(By.CSS_SELECTOR, "#loginForm > div > div.btn_wrap > a")
    driver.execute_script("arguments[0].click();", element)

    time.sleep(30)

    print(driver.current_url)


def get_address() -> str:
    driver.get(f"https://www.pocketcu.co.kr/event/main")

    time.sleep(30)

    items = driver.find_elements(By.XPATH, "//p[@class='tit_16']")
    for i, item in enumerate(items):
        if list(filter(lambda x: x in item.text, ["출석체크", "출석 체크", "출석룰렛"])):
            event_id = driver.find_element(
                By.CSS_SELECTOR, f"#contents > section > div.event_list > ul > li:nth-child({i+1}) > section > div > div.img_wrap"
            ).get_attribute("id")
            event_id = event_id[3:]
            print(event_id)
            return event_id


def attendance():
    time.sleep(30)

    now_count = driver.find_element(By.CSS_SELECTOR, "#myAttendCnt").text
    now_total = driver.find_element(By.CSS_SELECTOR, "#myAttendPoint").text
    print(now_count, now_total)

    element = driver.find_element(
        By.CSS_SELECTOR, "#contents > section > section > section.sub_wrap > div.event_area > div > div > div > div.roulette_main > div > div"
    )
    driver.execute_script("arguments[0].click();", element)

    time.sleep(30)

    driver.refresh()

    time.sleep(30)

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
