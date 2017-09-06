from bs4 import BeautifulSoup
import requests

def _parse_form_data(page_content, **additional_data):
    soup = BeautifulSoup(page_content, 'html.parser')
    form = soup.find('form')

    if form is None:
        return additional_data

    inputs = form.find_all('input', attrs={'disabled': False, 'value': lambda x: x != ''})

    if len(inputs) <= 0:
        return {}

    form_data = { input.get('name'): input.get('value') for input in inputs }
    form_data.update(additional_data)

    return form_data

def _get_password_prompt_url_from(username_validation_resp):
    validation_data = username_validation_resp.json()

    if "error" in validation_data and not validation_data["error"]:
        if "location" in validation_data:
            password_prompt_url = validation_data["location"]
            if "/challenge/recaptcha" in password_prompt_url:
                raise Exception("We are fucked. Yahoo is asking for CAPTCHA response for your username. This only happens to a few usernames. Nothing to do here *flies away*")

            return password_prompt_url

    if "render" in validation_data and "error" in validation_data["render"]:
        raise Exception("Oops. An error was encountered.", validation_data["render"]["error"])

    raise Exception("UnknownValidationException", validation_data)


def sign_in(username, password):
    YAHOO_LOGIN_URL = 'https://login.yahoo.com/m'
    headers = { "x-requested-with": "XMLHttpRequest", "origin": "https://login.yahoo.com", "referer": "https://login.yahoo.com/m" }

    with requests.Session() as yahoo_session:
        login_page_resp = yahoo_session.get(YAHOO_LOGIN_URL)
        payload = _parse_form_data(login_page_resp.content, username=username, passwd=password)

        username_validation_resp = yahoo_session.post(YAHOO_LOGIN_URL, cookies=login_page_resp.cookies, data=payload, headers=headers)
        password_prompt_url = _get_password_prompt_url_from(username_validation_resp)

        # TODO
        # password_prompt_resp = yahoo_session.get(password_prompt_url)


sign_in("gali@yahoo.com", "")

