import datetime
import json
import os
import re

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import BASE_URL, LOGIN_EMAIL_URL, LOGIN_LANDING_URL, LOGIN_METHOD, LOGIN_TIMEOUT, WINDOW_SIZE

load_dotenv()

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

# 모든 테스트 함수 docstring 첫 줄은 TC-<FEATURE>-<3자리> 형식이다(FEATURE는
# TC-PRODUCT-DETAIL처럼 하이픈을 포함할 수 있다). 이후 부가설명(" (Negative)" 등)은
# 매칭 대상에서 제외한다.
TC_ID_PATTERN = re.compile(r"^(TC-[A-Z]+(?:-[A-Z]+)*-\d{3})")
TC_ID_FALLBACK = "-"


def _extract_tc_id(item):
    doc = getattr(item, "function", None) and item.function.__doc__
    if not doc:
        return TC_ID_FALLBACK
    first_line = doc.strip().splitlines()[0].strip()
    match = TC_ID_PATTERN.match(first_line)
    return match.group(1) if match else TC_ID_FALLBACK


def pytest_runtest_setup(item):
    item.user_properties.append(("tc_id", _extract_tc_id(item)))


def pytest_html_results_table_header(cells):
    cells.insert(1, "<th>TC-ID</th>")


def pytest_html_results_table_row(report, cells):
    tc_id = dict(report.user_properties).get("tc_id", TC_ID_FALLBACK)
    cells.insert(1, f"<td>{tc_id}</td>")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
    if driver is None:
        return

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{item.name}_failed_{timestamp}.png"
    driver.save_screenshot(os.path.join(SCREENSHOTS_DIR, filename))


def _click_when_stable(driver, locator, timeout):
    # 요소가 element_to_be_clickable 조건을 만족해도 다른 요소에 가려져 있으면
    # 클릭이 가로채인다(구글 로그인 비밀번호 단계에서 실측 확인,
    # ElementClickInterceptedException). 요소가 찾아질 때까지 대기한 뒤 클릭하고,
    # 가려져서 클릭이 가로채이면 해당 요소가 보이도록 하단으로 스크롤한 뒤 다시
    # 찾아 클릭한다.
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
        element.click()


def _hide_webdriver_flag(driver):
    # 구글 로그인이 Selenium의 navigator.webdriver 플래그를 감지해
    # "브라우저 또는 앱이 안전하지 않을 수 있습니다"로 차단하는 것을 완화한다
    # (완전한 우회는 아니며, 계속 차단되면 재시도 없이 실패로 보고한다).
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )


@pytest.fixture(scope="function")
def driver(request):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    # 실제 구글 로그인 화면(_complete_google_login)을 그대로 통과해야 하는 테스트는
    # headless 모드에서 구글의 자동화 브라우저 탐지("브라우저 또는 앱이 안전하지 않을
    # 수 있습니다")에 차단된다(실측 확인, AUTOMATION_GUIDE 7.23절). 이 테스트들에는
    # @pytest.mark.requires_real_browser 마커를 붙여 CI에서도 headless를 적용하지
    # 않는다(실제 로컬 머신이라 화면이 떠도 문제없다).
    requires_real_browser = request.node.get_closest_marker("requires_real_browser") is not None
    if os.environ.get("CI") and not requires_real_browser:
        # GitHub Actions 러너는 디스플레이가 없어 일반 Chrome이 그대로 실행되지 않는다
        # (로컬 개발 환경에는 CI 환경변수가 없으므로 이 분기는 CI에서만 적용된다).
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    _hide_webdriver_flag(driver)
    # 기본 창 크기(약 1200x832)에서는 "같은 작품 굿즈" 캐러셀 카드가 서로 겹쳐
    # 클릭이 인접 카드에 가로채이는 문제가 있어, 일반 데스크톱 해상도로 명시한다.
    driver.set_window_size(*WINDOW_SIZE)
    yield driver
    driver.quit()


def _select_first_profile(driver):
    WebDriverWait(driver, LOGIN_TIMEOUT).until(EC.url_contains("/profile"))

    profile_avatar = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'img[alt="profile"]'))
    )
    profile_avatar.click()

    WebDriverWait(driver, LOGIN_TIMEOUT).until(lambda d: d.current_url != "https://laftel.net/profile")


def _agree_to_store_terms_if_present(driver):
    # 스토어를 처음 이용하는 계정은 "스토어 이용약관 동의" 모달이 뜬다(기존
    # 이메일 계정은 이미 동의한 상태라 겪지 않았던 신규 계정 전용 1회성 온보딩).
    driver.get(BASE_URL)
    try:
        agree_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[normalize-space(.)="동의하고 시작하기"]'))
        )
        agree_button.click()
    except TimeoutException:
        pass


def _login_with_email(driver):
    email = os.environ["TEST_ACCOUNT_EMAIL"]
    password = os.environ["TEST_ACCOUNT_PASSWORD"]

    driver.get(LOGIN_EMAIL_URL)

    email_input = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"]'))
    )
    email_input.send_keys(email)

    next_button = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, '//button[normalize-space(.)="다음"]'))
    )
    next_button.click()

    password_input = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]'))
    )
    password_input.send_keys(password)

    login_button = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, '//button[normalize-space(.)="로그인"]'))
    )
    login_button.click()

    _select_first_profile(driver)


def _complete_google_login(driver):
    # "구글로 시작" 버튼이 이미 화면에 보이는 상태(라프텔 로그인 랜딩 화면)에서부터
    # 로그인을 끝까지 완료한다. 찜 로그인 유도 팝업의 "로그인" 버튼도 동일한 랜딩
    # 화면(redirect_url 파라미터만 다름)으로 이동하므로 이 헬퍼를 재사용할 수 있다.
    email = os.environ["GOOGLE_ACCOUNT_EMAIL"]
    password = os.environ["GOOGLE_ACCOUNT_PASSWORD"]

    original_window = driver.current_window_handle

    google_button = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="구글로 시작"]'))
    )
    google_button.click()

    # 구글 로그인은 팝업 창(window.open)으로 열린다.
    WebDriverWait(driver, LOGIN_TIMEOUT).until(lambda d: len(d.window_handles) > 1)
    google_window = [h for h in driver.window_handles if h != original_window][0]
    driver.switch_to.window(google_window)
    _hide_webdriver_flag(driver)

    email_input = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.element_to_be_clickable((By.ID, "identifierId"))
    )
    email_input.send_keys(email)

    WebDriverWait(driver, LOGIN_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "identifierNext"))).click()

    # 비밀번호 입력란은 이메일 단계에서도 DOM에 숨겨진 채 존재하므로
    # presence가 아닌 visibility로 대기해야 한다.
    password_input = WebDriverWait(driver, LOGIN_TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
    )
    password_input.send_keys(password)

    _click_when_stable(driver, (By.ID, "passwordNext"), LOGIN_TIMEOUT)

    # 로그인이 성공하면 팝업 창이 자동으로 닫히고 원래 창이 laftel.net으로 리디렉션된다.
    WebDriverWait(driver, LOGIN_TIMEOUT).until(lambda d: len(d.window_handles) == 1)
    driver.switch_to.window(original_window)

    _select_first_profile(driver)


def _login_with_google(driver):
    driver.get(LOGIN_LANDING_URL)
    _complete_google_login(driver)


def _login_with_session_cookies(driver):
    # CI에서는 구글 로그인 UI를 직접 자동화하지 않고, scripts/export_session_cookies.py로
    # 로컬에서 미리 캡처해 GitHub Secret으로 저장해 둔 세션 쿠키를 주입한다
    # (AUTOMATION_GUIDE 16.1절). 쿠키를 추가하려면 먼저 해당 도메인 페이지에 있어야
    # 하므로 BASE_URL로 이동한 뒤 주입하고, 다시 이동해 세션을 반영한다.
    cookies = json.loads(os.environ["SESSION_COOKIES_JSON"])

    driver.get(BASE_URL)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get(BASE_URL)


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    if os.environ.get("SESSION_COOKIES_JSON"):
        _login_with_session_cookies(driver)
    elif LOGIN_METHOD == "google":
        _login_with_google(driver)
    else:
        _login_with_email(driver)

    _agree_to_store_terms_if_present(driver)

    yield driver
