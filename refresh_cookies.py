#!/usr/local/bin/python3
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait


# This interfaces with a webdriver server to log into the store page in the
# normal way, to refresh our cookies.
def log_in_and_get_cookies(driver_url, username="", password=""):

    # Strip the trailing slash from the driver URL.
    driver_url = driver_url.strip("/")

    # Check if there is an existing cookie cache file
    try:
        with open("cookies.json", "r") as f:
            all_cookies = json.loads(f.read())
    except FileNotFoundError:
        all_cookies = {}

    # Initialise a webdriver interface.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability("browserVersion", "103")
    # Set the resolution to 1280x1024 so we don't get the mobile version of the page
    chrome_options.add_argument("--window-size=1280,1024")
    driver = webdriver.Remote(
        command_executor=f"{driver_url}/wd/hub", options=chrome_options
    )

    # We need to load up the homepage first, so the cookies are associated with the domain properly.
    f = driver.get("https://www.woolworths.com.au")

    # Iterate over all_cookies and load them into selenium
    for key, value in all_cookies.items():
        driver.add_cookie({"name": key, "value": value})

    # Reload the page with cookies loaded
    f = driver.get("https://www.woolworths.com.au")

    # Check driver.page_source for indication that we're logged out. Log in if required.
    if "Log in / Signup" in driver.page_source:
        print("We're logged out, we need to log in.")
        try:
            login_button = WebDriverWait(driver, 5).until(
                lambda x: x.find_element(by=By.ID, value="wx-link-login-desktop")
            )
            login_button.click()

            username_box = WebDriverWait(driver, 5).until(
                lambda x: x.find_element(by=By.ID, value="loginForm-Email")
            )
            password_box = driver.find_element(by=By.ID, value="loginForm-Password")
            remember_me_tick = driver.find_element(
                by=By.CLASS_NAME, value="loginForm-rememberMe"
            )
            remember_me_tick.click()
            username_box.send_keys(username)
            password_box.send_keys(password + Keys.ENTER)
        except Exception as e:
            # Save a screenshot of the page
            driver.save_screenshot("login_error.png")
            with open("page.html", "w") as f:
                f.write(driver.page_source)
            raise (e)

    # TODO Replace this with something that confirms we're logged in
    driver.implicitly_wait(2)

    # Convert the cookies to a simple dict for saving.
    for cookie in driver.get_cookies():
        all_cookies["{}".format(cookie["name"])] = cookie["value"]

    # Save the cookies to disk.
    with open("cookies.json", "w") as f:
        f.write(json.dumps(all_cookies))

    driver.quit()
    return all_cookies
