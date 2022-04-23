import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from util.driver import driver

load_dotenv(verbose=True)


def login(address: str):
    driver.get(f"https://www.pocketcu.co.kr/login?referer_url={address}")

    driver.implicitly_wait(10)

    id = driver.find_element(By.XPATH, '//*[@id="loginId"]')
    id.send_keys(os.getenv("ID"))

    pw = driver.find_element(By.XPATH, '//*[@id="loginPwd"]')
    pw.send_keys(os.getenv("PW"))

    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[4]/a').click()


def get_address() -> str:
    driver.get(f"https://www.pocketcu.co.kr/event/main")

    driver.implicitly_wait(10)

    items = driver.find_elements(By.XPATH, '//*[@id="contents"]/section/div[2]/ul/li/section/div/div[2]/div/p[2]')
    for i, item in enumerate(items):
        if list(filter(lambda x: x in item.text, ["출석체크", "출석 체크"])):
            event_id = driver.find_element(By.XPATH, f"/html/body/div/div/div/section/div[2]/ul/li[{i+1}]/section/div/div[1]").get_attribute("id")
            event_id = event_id[3:]
            address = f"https://www.pocketcu.co.kr/event/eventView/{event_id}"
            return address


def attendance():
    driver.implicitly_wait(10)

    now_count = driver.find_element(By.XPATH, '//*[@id="myAttendCnt"]').text
    now_total = driver.find_element(By.XPATH, '//*[@id="myAttendPoint"]').text
    print(now_count, now_total)

    driver.find_element(By.XPATH, '//*[@id="contents"]/section/section/section[1]/div[2]/div/div[2]/div/div').click()

    driver.refresh()

    time.sleep(10)

    count = driver.find_element(By.XPATH, '//*[@id="myAttendCnt"]').text
    total = driver.find_element(By.XPATH, '//*[@id="myAttendPoint"]').text
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
    address = get_address()
    login(address)
    attendance()
    driver.quit()
