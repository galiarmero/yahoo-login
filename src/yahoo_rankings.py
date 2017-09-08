from bs4 import BeautifulSoup
import requests
from collections import namedtuple

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

def _parse_form_data(page_content, **additional_data):
    soup = BeautifulSoup(page_content, 'html.parser')
    form = soup.find('form')

    if form is None:
        return additional_data

    inputs = form.find_all('input', attrs={'disabled': False, 'value': lambda x: x != ''})
    submit_buttons = form.find_all('button', attrs={'type': 'submit'})

    form_data = {}
    if len(inputs) > 0:
        form_data = { input.get('name'): input.get('value') for input in inputs }
    if len(submit_buttons) > 0:
        form_data.update({ button.get('name'): button.get('value') for button in submit_buttons })
    form_data.update(additional_data)

    return form_data


def _get_password_authentication_url(username_auth_resp):
    validation_data = username_auth_resp.json()

    if "render" in validation_data and "error" in validation_data["render"]:
        raise Exception(MESSAGES['ERROR_USERNAME_VALIDATION'], validation_data["render"]["error"])

    if "error" in validation_data and not validation_data["error"] and "location" in validation_data:
        password_prompt_url = validation_data["location"]

        if YAHOO['CAPTCHA_CHALLENGE_PATH'] in password_prompt_url:
            raise Exception(MESSAGES['ERROR_CAPTCHA_CHALLENGE'])

        return password_prompt_url

    raise Exception(MESSAGES['ERROR_UNKNOWN'], validation_data)


def _is_password_valid(password_auth_resp):
    return (YAHOO['HEADER_LOCATION'] in password_auth_resp.headers
            and not password_auth_resp.headers[ YAHOO['HEADER_LOCATION'] ].startswith(YAHOO["PASSWORD_CHALLENGE_PATH"]))


def _build_yahoo_login_response(password_auth_resp):
    response_headers = password_auth_resp.headers
    yahoo_login = {
        'success': _is_password_valid(password_auth_resp),
        'redirect_location': response_headers['Location'],
        'timestamp': response_headers['Date'],
        'cookies': password_auth_resp.cookies
    }

    return yahoo_login


def _verify_username(session, username):
    login_page_resp = session.get(YAHOO['LOGIN_URL'])
    payload = _parse_form_data(login_page_resp.content, username=username)

    return session.post(YAHOO['LOGIN_URL'], cookies=login_page_resp.cookies, data=payload,
                                            headers=YAHOO['XHR_HEADER'])

def _verify_password(session, authentication_url, password):
    password_page_resp = session.get(authentication_url)
    payload = _parse_form_data(password_page_resp.content, password=password)

    return session.post(authentication_url, cookies=password_page_resp.cookies, data=payload,
                                            allow_redirects=False)


def sign_in(username, password):
    with requests.Session() as yahoo_session:
        username_auth_resp = _verify_username(yahoo_session, username)
        authentication_url = _get_password_authentication_url(username_auth_resp)
        password_auth_resp = _verify_password(yahoo_session, authentication_url, password)

        return _build_yahoo_login_response(password_auth_resp)


sign_in("foo", "bar")

