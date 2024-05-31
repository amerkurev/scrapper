# Scrapper 🧹

<div markdown="1">
[![Build](https://github.com/amerkurev/scrapper/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/amerkurev/scrapper/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/amerkurev/scrapper/badge.svg?branch=master)](https://coveralls.io/github/amerkurev/scrapper?branch=master)
[![Linting: Pylint](https://img.shields.io/badge/pylint-9.95-green)](https://github.com/amerkurev/scrapper/actions/)
[![License](https://img.shields.io/badge/license-apache2.0-blue.svg)](https://github.com/amerkurev/scrapper/blob/master/LICENSE)
[![Docker Hub](https://img.shields.io/docker/automated/amerkurev/scrapper.svg)](https://hub.docker.com/r/amerkurev/scrapper/tags)
</div>

If you were looking for a web scraper that actually works, you just found it. It's called Scrapper!
Downloading a page from the Internet and then extracting an article from it in a structured format is not as easy as it may seem at first glance.
Sometimes it can be damn hard. But Scrapper will help you with this, I hope :) To do this, Scrapper has plenty of features.

Scrapper is a free and open-source product. It combines the power and experience of related open-source projects, so give it a try first.

## Quick start
Quick start a scrapper instance:
```console
docker run -d -p 3000:3000 --name scrapper amerkurev/scrapper:latest
```
Scrapper will be available at [http://localhost:3000/](http://localhost:3000/). For more details, see [Usage](/sections/usage/)

## Demo
Watch a 30-second demo reel showcasing the web interface of Scrapper.

<video style='border: 1px solid #1e2129;' controls>
<source src="https://user-images.githubusercontent.com/28217522/225941167-633576fa-c9e2-4c63-b1fd-879be2d137fa.mp4" type="video/mp4">
</video>

## Features
The main features of Scrapper are:

- **The headless browser is already built-in.** Modern websites actively use JavaScript on their pages, fight against crawlers, and sometimes require user actions, such as agreeing to the use of cookies on the site. All of these tasks are solved by the Scrapper using the excellent [Playwright](https://github.com/microsoft/playwright) project. The Scrapper container image is based on the Playwright image, which already includes all modern browsers.
- **The Read mode in the browser is used for parsing.** Millions of people use the "Read" mode in the browser to display only the text of the article on the screen while hiding the other elements of the page. Scrapper follows the same path by using the excellent [Readability.js](https://github.com/mozilla/readability) library from Mozilla. The parsing result will be the same as in the [Read mode](https://support.mozilla.org/kb/firefox-reader-view-clutter-free-web-pages) of your favorite browser.
- **A simple and beautiful web interface.** Working with Scrapper is easy and enjoyable because you can do it right in your browser. The simple web interface allows you to debug your query, experiment with each parameter in the API, and see the result in HTML, JSON, or a screenshot. The beautiful design helps achieve an excellent [Pico](https://github.com/picocss/pico) project. A dark theme for comfortable reading is also available.
- **The Scrapper REST API is incredibly simple** to use as it only requires a [single call](/sections/api) and just a few parameters making it easy to integrate into any project. Furthermore, the web interface offers a visual query-builder that simplifies the learning process for the user.
- **Scrapper can search for news links** on the main pages of websites. This is difficult because there may be not only links to news but also links to other parts of the website. However, Scrapper can distinguish between them and select only links to news articles.

And many other features:

- **Stealth mode.** Various methods are used to make it difficult for websites to detect a Headless browser and bypass web scraping protection.
- **Caching results.** All parsing results are saved to disk, and you can access them later by API without repeating the whole request.
- **Page screenshots.** Headless browsers don't have a window, but screenshots allow you to see the page as it appears to the parser. This is very useful!
- **Incognito mode or persistent sessions.** You can configure the browser to work in incognito mode or without it. In this case, the browser will save session data such as cookies and local storage to disk. To use them again.
- **Proxy support.** HTTP/SOCKS4/SOCKS5 proxy work is supported.
- **Fully customizable.** You can control a lot through the API: additional HTTP headers, viewport for device emulation, Readability parser settings, and much more.
- **Delivered as a Docker image.** Scrapper is built and delivered as a Docker image, which is very easy to deploy for testing and production. No dependencies or installations on the host. All you need to run Scrapper is Docker.
- **Free license.** Scrapper doesn't ask for money, insert ads, or track your actions ever. And if you want to help the project develop further, just give us a star on GitHub ⭐

## Supported architectures

- linux/amd64
- linux/arm64

## Status
The project is under active development and may have breaking changes till `v1` is released. 
However, we are trying our best not to break things unless there is a good reason. As of version `v0.8.0`, Scrapper is considered good enough for real-life usage, and many setups are running it in production.

## License
[Apache-2.0 license](https://github.com/amerkurev/scrapper/blob/master/LICENSE)
