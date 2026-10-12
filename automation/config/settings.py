BASE_URL = "https://store.laftel.net/"
DEFAULT_TIMEOUT = 10
LOGIN_TIMEOUT = 20
LOGIN_EMAIL_URL = "https://laftel.net/auth/email"
LOGIN_LANDING_URL = "https://laftel.net/auth/login"
# 이메일 로그인 계정(TEST_ACCOUNT_*)이 서버측 잠금으로 추정되는 오류로 막혀
# 임시로 구글 로그인으로 전환(AUTOMATION_GUIDE 7.7 참고). 잠금 해제 후 "email"로 원복.
LOGIN_METHOD = "google"
WINDOW_SIZE = (1600, 1000)
