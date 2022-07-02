#!/usr/local/bin/python3
import toml
import json, time, requests
from pprint import pprint
from refresh_cookies import log_in_and_get_cookies

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


class woolworths_api:
    s: requests.Session
    items: dict
    config: dict

    def __init__(self):
        # Attempt to load the config from config_real.toml, which isn't checked into source control.
        # Failing that, load the example config file.
        try:
            with open("config_real.toml") as f:
                self.config = toml.load(f)
        except FileNotFoundError:
            with open("config.toml") as f:
                self.config = toml.load(f)

    def __enter__(self):
        self.items = {}
        all_cookies = log_in_and_get_cookies(
            self.config["webdriver_url"],
            self.config["username"],
            self.config["password"],
        )
        # Set up a scraping session.
        self.s = requests.Session()
        self.s.cookies.update(all_cookies)
        self.s.headers.update(headers)

        print("Logged in to API")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO Consider logging out.
        r = self.s.post('https://www.woolworths.com.au/apis/ui/Logout')
        if r.status_code != 200 or not r.json()['Success']:
            print("Logout failed:")
            print(r.text)
            exit(1)
        print("Logged out of the API")

    # Add an item to the shopping cart
    def add_stockcode_to_cart(self, stockcode, count=1):
        payload = {
            "items": [
                {
                    "stockcode": stockcode,
                    "diagnostics": "0",
                    "quantity": count,
                    "source": "ProductGroup.290622-wk1-household-personal-care-offertile",
                    "offerId": None,
                    "searchTerm": None,
                    "profileId": None,
                    "priceLevel": None,
                },
            ],
        }
        r = self.s.post(
            "https://www.woolworths.com.au/api/v3/ui/trolley/update", json=payload
        )
        if r.status_code != 200:
            print("Add failed:")
            print(r.text)
            return False
        if r.text:
            for u in r.json()["UpdatedItems"]:
                print(u["DisplayName"])
        return True

    # Remove an item from the cart
    def remove_stockcode_from_cart(self, stockcode):
        return self.add_stockcode_to_cart(stockcode, 0)

    # Read the current contents of the shopping cart
    def update_cart(self):
        r = self.s.get("https://www.woolworths.com.au/apis/ui/Trolley")
        if r.status_code != 200:
            print("Get cart failed:")
            print(r.text)
            return False
        # print(r.text)
        self.items = r.json()["AvailableItems"]
        return True

if __name__ == "__main__":
    with woolworths_api() as w:
        w.update_cart()
        print("Items in cart:")
        print("--------")
        for item in w.items:
            print(f"{item['Quantity']} x {item['Name']}")
        print("--------")
        w.add_stockcode_to_cart(41285, 2)  # Some margarine
        w.add_stockcode_to_cart(500187, 2)  # Some cheese
        w.update_cart()

        print("Items in cart:")
        print("--------")
        for item in w.items:
            print(f"{item['Quantity']} x {item['Name']}")
        print("--------")
        w.remove_stockcode_from_cart(500187)
        w.update_cart()

        print("Items in cart:")
        print("--------")
        for item in w.items:
            print(f"{item['Quantity']} x {item['Name']}")
        print("--------")
