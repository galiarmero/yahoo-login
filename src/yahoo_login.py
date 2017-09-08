import requests

from auth_session import AuthSession
import page_parser

YAHOO = {
    "HOME_URL": "https://www.yahoo.com/",
    "LOGIN_URL": "https://login.yahoo.com/m",
    "XHR_HEADER": {
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://login.yahoo.com"
    },
    "CAPTCHA_CHALLENGE_PATH": "/account/challenge/recaptcha",
    "PASSWORD_CHALLENGE_PATH": "/account/challenge/password",
    "HEADER_LOCATION": "Location"
}

MESSAGES = {
    "ERROR_CAPTCHA_CHALLENGE": "We are fucked. Yahoo is asking for CAPTCHA response for your username. "
                               "This happens every so often to some accounts. Try again next time. Nothing to do here "
                               "*flies away*",
    "ERROR_USERNAME_VALIDATION": "Oops. Yahoo responded with an error",
    "ERROR_UNKNOWN": "Something went wrong."
}

class YahooLogin(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._sign_in()

    def session(self):
        return AuthSession(self._session)

    def _sign_in(self):
        username_auth_resp = self._verify_username()
        authentication_url = self._get_password_authentication_url(username_auth_resp)
        password_auth_resp = self._verify_password(authentication_url)

        if not self._is_password_valid:
            self._session.close()
            raise Exception("Invalid password")


    def _verify_username(self):
        login_page_resp = self._session.get(YAHOO['LOGIN_URL'])
        payload = page_parser.parse_form_data(login_page_resp.content, username=self._username)

        return self._session.post(YAHOO['LOGIN_URL'], cookies=login_page_resp.cookies, data=payload,
                                                        headers=YAHOO['XHR_HEADER'])


    def _verify_password(self, authentication_url):
        password_page_resp = self._session.get(authentication_url)
        payload = page_parser.parse_form_data(password_page_resp.content, password=self._password)

        return self._session.post(authentication_url, cookies=password_page_resp.cookies, data=payload,
                                                        allow_redirects=False)


    def _get_password_authentication_url(self, username_auth_resp):
        validation_data = username_auth_resp.json()

        if "render" in validation_data and "error" in validation_data["render"]:
            raise Exception(MESSAGES['ERROR_USERNAME_VALIDATION'], validation_data["render"]["error"])

        if "error" in validation_data and not validation_data["error"] and "location" in validation_data:
            password_prompt_url = validation_data["location"]

            if YAHOO['CAPTCHA_CHALLENGE_PATH'] in password_prompt_url:
                raise Exception(MESSAGES['ERROR_CAPTCHA_CHALLENGE'])

            return password_prompt_url

        raise Exception(MESSAGES['ERROR_UNKNOWN'], validation_data)

    def _is_password_valid(self, password_auth_resp):
        return (YAHOO['HEADER_LOCATION'] in password_auth_resp.headers
                and not password_auth_resp.headers[ YAHOO['HEADER_LOCATION'] ].startswith(YAHOO["PASSWORD_CHALLENGE_PATH"]))


