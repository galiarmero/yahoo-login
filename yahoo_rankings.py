from bs4 import BeautifulSoup
import requests

def _parse_form_data(page_content, username, password):
    soup = BeautifulSoup(page_content, 'html.parser')
    form = soup.find('form')
    inputs = form.find_all('input', attrs={'disabled': False, 'value': lambda x: x != ''})

    form_data = { input.get('name'): input.get('value') for input in inputs }
    form_data.update({ 'username': username, 'passwd': password })

def sign_in(username, password):
    YAHOO_LOGIN_URL = 'https://login.yahoo.com/m'

    with requests.Session() as yahooSession:
        resp = yahooSession.get(YAHOO_LOGIN_URL)
        _parse_form_data(resp.content, username, password)


sign_in("gali", "hehe")

