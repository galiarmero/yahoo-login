from yahoo_login import YahooLogin

def trial(username, password):
    with YahooLogin(username, password).session() as yahoo_session:
        resp = yahoo_session.get("https://www.yahoo.com")
        
        print(resp.content)


trial("foo", "bar")
