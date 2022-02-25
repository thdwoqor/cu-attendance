import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.driver import driver


def login(address: str):
    try:
        driver.get(address)

        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[1]/div[1]/div/div[3]/div[3]/button")))

        id = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[1]/div/div[3]/div[1]/input")
        id.send_keys(str(sys.argv[1]))

        pw = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[1]/div/div[3]/div[2]/input")
        pw.send_keys(str(sys.argv[2]))

        driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[1]/div/div[3]/div[3]/button").click()
    except:
        login(address)


def get_address() -> str:
    for i in range(1, 10):
        driver.get(f"https://apmembership.bgfretail.com/pc/eventList?sType=&state=&page={i}")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="contents"]/div[3]/div[3]')))
        items = driver.find_elements(By.XPATH, '//*[@id="contents"]/div[3]/div[3]/ul/li/h4')
        for i, item in enumerate(items):
            if list(filter(lambda x: x in item.text, ["출석 룰렛", "출석룰렛"])):
                event_id = driver.find_element(By.XPATH, f'//*[@id="contents"]/div[3]/div[3]/ul/li[{i+1}]/div/img').get_attribute("data-event_id")
                return f"https://apmember.bgfretail.com/pc/login?service=https%3A%2F%2Fapmembership.bgfretail.com%2Fpc%2FeventDetail%3Fevent_id%3D{event_id}"


def attendance(address: str):
    count, total, point = 0, 0, 0
    try:
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="play"]')))
        driver.find_element(By.XPATH, '//*[@id="play"]').click()
        time.sleep(10)
        count = driver.find_element(By.XPATH, '//*[@id="myAttendCnt"]').text
        total = driver.find_element(By.XPATH, '//*[@id="myAttendPoint"]').text
        point = driver.find_element(By.XPATH, '//*[@id="rouletteResultText"]').text
    except:
        driver.get(address)
        attendance()


if __name__ == "__main__":
    address = get_address()
    login(address)
    attendance(address)
    driver.quit()
