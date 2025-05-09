#!/usr/local/bin/python3
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait


def log_in(driver, username, password):
    # Check the logged in indicator to determine whether we need to log in.
    login_indicator = WebDriverWait(driver, 5).until(
        lambda x: x.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/section/button[2]/div/span")
    )

    if "My Account" in login_indicator.text:
        return True

    login_button = WebDriverWait(driver, 5).until(
        lambda x: x.find_element(by=By.ID, value="wx-link-login-desktop")
    )
    login_button.click()
    # while "Problem in Aisle 6!" in driver.find_element(by=By.XPATH, value="/html/body/wow-root/wow-app-layout/div/div/main/wow-error-container/div/div/h1").text:
    while "Problem in Aisle 6!" in driver.page_source:
        time.sleep(0.5)
        login_button.click()
        print("Clicking login again")
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

    # Wait until we're logged in
    timeout = time.time() + 5
    while time.time() < timeout:
        if "My Account" in login_indicator.text:
            return True
        time.sleep(0.1)
    else:
        print("Failed to refresh cookies.")
        driver.save_screenshot("refresh_fail.png")

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
    chrome_options.add_argument("--window-size=1600,1024")
    driver = webdriver.Remote(
        command_executor=f"{driver_url}/wd/hub", options=chrome_options
    )

    # We need to load up the homepage first, so the cookies are associated with the domain properly.
    f = driver.get("https://www.woolworths.com.au")

    # Iterate over all_cookies and load them into selenium
    for key, value in all_cookies.items():
        driver.add_cookie({"name": key, "value": value})

    # Reload the page with cookies loaded
    driver.get("https://google.com.au")
    driver.get("https://www.woolworths.com.au")


    if "My Account" not in login_indicator.text:
        print("We're logged out, we need to log in.")
        try:
           log_in(driver, username, password)
        except Exception as e:
            # Save a screenshot of the page
            driver.save_screenshot("login_error.png")
            with open("page.html", "w") as f:
                f.write(driver.page_source)
            raise (e)

    # Convert the cookies to a simple dict for saving.
    for cookie in driver.get_cookies():
        all_cookies["{}".format(cookie["name"])] = cookie["value"]

    # Save the cookies to disk.
    with open("cookies.json", "w") as f:
        f.write(json.dumps(all_cookies))

    driver.quit()
    return all_cookies
