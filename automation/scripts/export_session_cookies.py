import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv  # noqa: E402
from selenium import webdriver  # noqa: E402

from conftest import _complete_google_login, _hide_webdriver_flag  # noqa: E402
from config.settings import BASE_URL, LOGIN_LANDING_URL, WINDOW_SIZE  # noqa: E402

load_dotenv()


def main():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(*WINDOW_SIZE)
        _hide_webdriver_flag(driver)
        driver.get(LOGIN_LANDING_URL)
        _complete_google_login(driver)

        # 인증 쿠키는 .laftel.net 상위 도메인에 저장되어 store.laftel.net에도
        # 공유되므로(실측 확인), store.laftel.net에서 조회한 쿠키 집합이면 충분하다.
        driver.get(BASE_URL)
        cookies = driver.get_cookies()

        # 세션 쿠키는 민감정보이므로 파일로 저장하지 않고 표준출력에만 JSON으로
        # 출력한다. 이 값을 그대로 복사해 GitHub Secret(SESSION_COOKIES_JSON)에
        # 등록한다.
        print(json.dumps(cookies))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
