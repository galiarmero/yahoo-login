from bs4 import BeautifulSoup

def parse_form_data(page, **additional_data):
    soup = BeautifulSoup(page, 'html.parser')
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