# Woolworths.com.au interface

This is a python interface to the woolworths.com.au website. It is intended to be a part of a system that automates grocery ordering from Grocy. This interface is not very robust. It depends on a selenium webdriver instance logging into the page to cache cookies, because the API depends on them. The initial login may require a 2FA SMS code. I suggest you do this interactively in a browser, extract the cookies from your browser storage and paste it into `cookies.json` to bootstrap the login. This cache will be overwritten with every interface login to keep things fresh.

## Configuration

Copy `config.toml` to `config_real.toml`. Edit the values in `config_real.toml` so you don't accidentally check your secrets into source control.

You'll need to set up a webdriver server. This can be done easily with docker-compose:

```yaml
  webdriver-browser-chrome:
    image: selenium/standalone-chrome-debug:3.141.59
    ports:
      - 4444:4444 # This doesn't actually do anything.
    environment:
      - VNC_NO_PASSWORD=1
      - SCREEN_WIDTH=1920
      - SCREEN_HEIGHT=1080
      - SCREEN_DEPTH=24
    volumes:
      # Workaround to avoid the browser crashing inside a docker container
      # See https://github.com/SeleniumHQ/docker-selenium#quick-start
      - /dev/shm:/dev/shm
    restart: unless-stopped
```



