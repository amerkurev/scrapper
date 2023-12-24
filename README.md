# Scrapper 🧹
<div>

[![Build](https://github.com/amerkurev/scrapper/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/amerkurev/scrapper/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/amerkurev/scrapper/badge.svg?branch=master)](https://coveralls.io/github/amerkurev/scrapper?branch=master)
[![License](https://img.shields.io/badge/license-apache2.0-blue.svg)](https://github.com/amerkurev/scrapper/blob/master/LICENSE)
[![Docker Hub](https://img.shields.io/docker/automated/amerkurev/scrapper.svg)](https://hub.docker.com/r/amerkurev/scrapper/tags)
</div>

If you were looking for a web scraper that actually works, you just found it. It's called Scrapper! Downloading a page from the Internet and then extracting an article from it in a structured format is not as easy as it may seem at first glance. Sometimes it can be damn hard. But Scrapper will help you with this, I hope :) To do this, Scrapper has plenty of features.

Yes, of course, you can use commercial services for your tasks, but Scrapper has been and will always be completely free for you. Scrapper has combined all the power and experience of related Open Source projects, so first, try it out.

<details>
  <summary><b>Quick start</b></summary>

Quick start a scrapper instance:
```console
docker run -d -p 3000:3000 --name scrapper amerkurev/scrapper:latest
```
Scrapper will be available at http://localhost:3000/. For more details, see [Usage](#usage)
</details>

## Demo
Watch a 30-second demo reel showcasing the web interface of Scrapper.

https://user-images.githubusercontent.com/28217522/225941167-633576fa-c9e2-4c63-b1fd-879be2d137fa.mp4


## Features
The main features of Scrapper are:
- **The headless browser is already built-in.** Modern websites actively use JavaScript on their pages, fight against crawlers, and sometimes require user actions, such as agreeing to the use of cookies on the site. All of these tasks are solved by the Scrapper using the excellent [Playwright](https://github.com/microsoft/playwright) project. The Scrapper container image is based on the Playwright image, which already includes all modern browsers.
- **The Read mode in the browser is used for parsing.** Millions of people use the "Read" mode in the browser to display only the text of the article on the screen while hiding the other elements of the page. Scrapper follows the same path by using the excellent [Readability.js](https://github.com/mozilla/readability) library from Mozilla. The parsing result will be the same as in the [Read mode](https://support.mozilla.org/kb/firefox-reader-view-clutter-free-web-pages) of your favorite browser.
- **A simple and beautiful web interface.** Working with Scrapper is easy and enjoyable because you can do it right in your browser. The simple web interface allows you to debug your query, experiment with each parameter in the API, and see the result in HTML, JSON, or a screenshot. The beautiful design helps achieve an excellent [Pico](https://github.com/picocss/pico) project. A dark theme for comfortable reading is also available.
- **The Scrapper REST API is incredibly simple** to use as it only requires a [single call](#api-reference) and just a few parameters making it easy to integrate into any project. Furthermore, the web interface offers a visual query-builder that simplifies the learning process for the user.
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


## Usage
### Getting Scrapper
The Scrapper Docker image is based on the Playwright image, which includes all the dependencies needed to run a browser in Docker and also includes the browsers themselves. As a result, the image size is quite large, around 2 GB. Make sure you have enough free disk space, especially if you plan to take and store screenshots frequently. To get the latest version of Scrapper, run:
```console
docker pull amerkurev/scrapper:latest
```

### Creating directories
Scrapper uses two directories on the disk. The first one is the `user_data_dir` directory. This directory contains browser session data such as cookies and local storage. Additionally, the cache of Scrapper's own results (including screenshots) is stored in this directory.

The second directory is `user_scripts`. In this directory, you can place your own JavaScript scripts, which you can then embed on pages through the Scrapper API. For example, to remove ads blocks or click the "Accept Cookies" button (see the `user-scripts` parameter in the [API Reference](#api-reference) section for more information).

**Scrapper does not work from the root** user inside the container. Instead, it uses a user with UID `1001`. Since you will be mounting the `user_data_dir` and `user_scripts` directories from the host using [Bind Mount](https://docs.docker.com/storage/bind-mounts/), you will need to set write permissions for UID `1001` on these directories on the host. 

Here is an example of how to do this:
```console
mkdir -p user_data_dir user_scripts

chown 1001:1001 user_data_dir/ user_scripts/

ls -l
```
The last command (`ls -l`) should output a result similar to this:
```
drwxr-xr-x 2 1001 1001 4096 Mar 17 23:23 user_data_dir
drwxr-xr-x 2 1001 1001 4096 Mar 17 23:23 user_scripts
```
<b>Important implementation details</b>. Over time, the Scrapper cache will grow, especially if you frequently request screenshots. Currently, there is no automatic data clearing in the cache, so keep an eye on the `user_data_dir/_res` directory if disk space starts to run low.

### Using Scrapper
Once the directories have been created and write permissions have been set, you can run Scrapper using the following command:
```console
docker run -d -p 3000:3000 -v $(pwd)/user_data_dir:/home/user/user_data_dir -v $(pwd)/user_scripts:/home/user/user_scripts --name scrapper amerkurev/scrapper:latest
```
The Scrapper web interface should now be available at http://localhost:3000/. Use any modern browser to access it.

To connect to Scrapper logs, use the following command:
```console
docker logs -f scrapper
```

## API Reference
### GET /api/article?url=...
The Scrapper API is very simple. Essentially, it is just one call that can easily be demonstrated using the cURL:

```console
curl -X GET "localhost:3000/api/article?url=https://en.wikipedia.org/wiki/web_scraping"
```

Use the GET method on the `/api/article` endpoint, passing one required parameter `url`. This is the full URL of the webpage on the Internet that contains an article. Scrapper will load the webpage in a browser, extract the article text, and return it in JSON format in the response.

All other request parameters are optional and have default values. However, you can customize them to your liking. The table below lists all the parameters that you can use, along with their descriptions and default values. To make it easier to build requests, use the web interface where the final request link is generated in real-time as you configure the parameters.

### Request Parameters

#### Scrapper settings
| Parameter                 | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Default |
|:--------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
| `url`                     | Page URL. The page should contain the text of the article that needs to be extracted.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |         |
| `cache`                   | All results of the parsing process will be cached in the `user_data_dir` directory. Cache can be disabled by setting the cache option to false. In this case, the page will be fetched and parsed every time. Cache is enabled by default.                                                                                                                                                                                                                                                                                                                                                                                                                                        | `true`  |
| `full-content`            | If this option is set to true, the result will have the full HTML contents of the page (`fullContent` field in the response).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | `false` |
| `stealth`                 | Stealth mode allows you to bypass anti-scraping techniques. It is disabled by default.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | `false` |
| `screenshot`              | If this option is set to true, the result will have the link to the screenshot of the page (`screenshot` field in the response). <b>Important implementation details</b>: Initially, Scrapper attempts to take a screenshot of the entire scrollable page. If it fails because the image is too large, it will only capture the currently visible viewport.                                                                                                                                                                                                                                                                                                                       | `false` |
| `user-scripts`            | To use your JavaScript scripts on the page, add script files to the `user_scripts` directory, and list the required ones (separated by commas) in the `user-scripts` parameter. These scripts will execute after the page loads but before the article parser runs. This allows you to help parse the article in a variety of ways, such as removing markup, ad blocks, or anything else. For example: `user-scripts=remove_ads.js, click_cookie_accept_button.js`. If you plan to run asynchronous long-running scripts, check --user-scripts-timeout parameter.<br/> Keep in mind that name of the script cannot contain commas because it will be parsed as a list of scripts. |         |
| `user-scripts-timeout`    | Waits for the given timeout in milliseconds after users scripts injection. For example if you want to navigate through page to specific content, set a longer period (higher value). The default value is 0, which means no sleep.                                                                                                                                                                                                                                                                                                                                                                                                                                                | `0`     |

#### Browser settings
| Parameter              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Default            |
|:-----------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------|
| `incognito`            | Allows creating `incognito` browser contexts. Incognito browser contexts don't write any browsing data to disk.                                                                                                                                                                                                                                                                                                                                                                                                        | `true`             |
| `timeout`              | Maximum operation time to navigate to the page in milliseconds; defaults to 60000 (60 seconds). Pass 0 to disable the timeout.                                                                                                                                                                                                                                                                                                                                                                                         | `60000`            |
| `wait-until`           | When to consider navigation succeeded, defaults to `domcontentloaded`. Events can be either:<br/>`load` - consider operation to be finished when the `load` event is fired.<br/>`domcontentloaded` - consider operation to be finished when the DOMContentLoaded event is fired.<br/>`networkidle` - consider operation to be finished when there are no network connections for at least 500 ms.<br/>`commit` - consider operation to be finished when network response is received and the document started loading. | `domcontentloaded` |
| `sleep`                | Waits for the given timeout in milliseconds before parsing the article, and after the page has loaded. In many cases, a sleep timeout is not necessary. However, for some websites, it can be quite useful. Other waiting mechanisms, such as waiting for selector visibility, are not currently supported. The default value is 0, which means no sleep.                                                                                                                                                              | `0`                |
| `resource`             | List of resource types allowed to be loaded on the page. All other resources will not be allowed, and their network requests will be aborted. **By default, all resource types are allowed.** The following resource types are supported: `document`, `stylesheet`, `image`, `media`, `font`, `script`, `texttrack`, `xhr`, `fetch`, `eventsource`, `websocket`, `manifest`, `other`. Example: `document,stylesheet,fetch`.                                                                                            |                    |
| `viewport-width`       | The viewport width in pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `414`              |
| `viewport-height`      | The viewport height in pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `896`              |
| `screen-width`         | The page width in pixels. Emulates consistent window screen size available inside web page via window.screen. Is only used when the viewport is set.                                                                                                                                                                                                                                                                                                                                                                   | `828`              |
| `screen-height`        | The page height in pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `1792`             |
| `scroll-down`          | Scroll down the page by a specified number of pixels. This is particularly useful when dealing with lazy-loading pages (pages that are loaded only as you scroll down). This parameter is used in conjunction with the `sleep` parameter. Make sure to set a positive value for the `sleep` parameter, otherwise, the scroll function won't work.                                                                                                                                                                      | `0`                |
| `ignore-https-errors`  | Whether to ignore HTTPS errors when sending network requests. The default setting is to ignore HTTPS errors.                                                                                                                                                                                                                                                                                                                                                                                                           | `true`             |
| `user-agent`           | Specific user agent.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                    |
| `locale`               | Specify user locale, for example en-GB, de-DE, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting rules.                                                                                                                                                                                                                                                                                                                                     |                    |
| `timezone`             | Changes the timezone of the context. See ICU's metaZones.txt for a list of supported timezone IDs.                                                                                                                                                                                                                                                                                                                                                                                                                     |                    |
| `http-credentials`     | Credentials for HTTP authentication (string containing username and password separated by a colon, e.g. `username:password`).                                                                                                                                                                                                                                                                                                                                                                                          |                    |
| `extra-http-headers`   | Contains additional HTTP headers to be sent with every request. Example: `X-API-Key:123456;X-Auth-Token:abcdef`.                                                                                                                                                                                                                                                                                                                                                                                                       |                    |

#### Network proxy settings
| Parameter                | Description                                                                                                                                                                                         | Default |
|:-------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
| `proxy-server`           | Proxy to be used for all requests. HTTP and SOCKS proxies are supported, for example http://myproxy.com:3128 or socks5://myproxy.com:3128. Short form myproxy.com:3128 is considered an HTTP proxy. |         |
| `proxy-bypass`           | Optional comma-separated domains to bypass proxy, for example `.com, chromium.org, .domain.com`.                                                                                                    |         |
| `proxy-username`         | Optional username to use if HTTP proxy requires authentication.                                                                                                                                     |         |
| `proxy-password`         | Optional password to use if HTTP proxy requires authentication.                                                                                                                                     |         |

#### Readability settings
| Parameter                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Default |
|:-------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
| `max-elems-to-parse`     | The maximum number of elements to parse. The default value is 0, which means no limit.                                                                                                                                                                                                                                                                                                                                                                         | 0       |
| `nb-top-candidates`      | The number of top candidates to consider when analysing how tight the competition is among candidates.                                                                                                                                                                                                                                                                                                                                                         | 5       |
| `char-threshold`         | The number of characters an article must have in order to return a result.                                                                                                                                                                                                                                                                                                                                                                                     | 500     |

### Response fields
The response to the `/api/article` request returns a JSON object that contains fields, which are described in the table below.

| Parameter       | Description                                                         | Type        |
|:----------------|:--------------------------------------------------------------------|:------------|
| `byline`        | author metadata                                                     | null or str |
| `content`       | HTML string of processed article content                            | null or str |
| `dir`           | content direction                                                   | null or str |
| `excerpt`       | article description, or short excerpt from the content              | null or str |
| `fullContent`   | full HTML contents of the page                                      | null or str |
| `id`            | unique result ID                                                    | str         |
| `url`           | page URL after redirects, may not match the query URL               | str         |
| `domain`        | page's registered domain                                            | str         |
| `lang`          | content language                                                    | null or str |
| `length`        | length of extracted article, in characters                          | null or int |
| `date`          | date of extracted article in ISO 8601 format                        | str         |
| `query`         | request parameters                                                  | object      |
| `meta`          | social meta tags (open graph, twitter)                              | object      |
| `resultUri`     | URL of the current result, the data here is always taken from cache | str         |
| `screenshotUri` | URL of the screenshot of the page                                   | null or str |
| `siteName`      | name of the site                                                    | null or str |
| `textContent`   | text content of the article, with all the HTML tags removed         | null or str |
| `title`         | article title                                                       | null or str |
| `publishedTime` | article publication time                                            | null or str |

### Error handling
If an error (or multiple errors) occurs during the execution of a request, the response structure will be as follows:
```json
{
  "detail": [
    {
      "type": "error_type",
      "msg": "some message"
    }
  ]
}
```
Some errors do not have a detailed description in the response to the request. In this case, you should refer to the log of the Docker container to investigate the cause of the error.

### GET /api/links?url=...
To collect links to news articles on the main pages of websites, use a different query on the `/api/links` endpoint. The query parameters are similar, but the [Readability settings](#readability-settings) are not required for this query because no text is extracted. Instead, the Link parser is used, which has its own set of parameters. A description of these parameters is provided below.

```console
curl -X GET "localhost:3000/api/links?url=https://www.cnet.com/"
```

#### Link parser settings
| Parameter               | Description                                                                                                                                                                                                                                                         | Default |
|:------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
| `text-len-threshold`    | The median (middle value) of the link text length in characters. The default value is 40 characters. Hyperlinks must adhere to this criterion to be included in the results. However, this criterion is not a strict threshold value, and some links may ignore it. | 40      |
| `words-threshold`       | The median (middle value) of the number of words in the link text. The default value is 3 words. Hyperlinks must adhere to this criterion to be included in the results. However, this criterion is not a strict threshold value, and some links may ignore it.     | 3       |

### Response fields
The response to the `/api/links` request returns a JSON object that contains fields, which are described in the table below.

| Parameter       | Description                                                         | Type     |
|:----------------|:--------------------------------------------------------------------|:---------|
| `fullContent`   | full HTML contents of the page                                      | str      |
| `id`            | unique result ID                                                    | str      |
| `url`           | page URL after redirects, may not match the query URL               | str      |
| `domain`        | page's registered domain                                            | str      |
| `date`          | date when the links were collected in ISO 8601 format               | str      |
| `query`         | request parameters                                                  | object   |
| `meta`          | social meta tags (open graph, twitter)                              | object   |
| `resultUri`     | URL of the current result, the data here is always taken from cache | str      |
| `screenshotUri` | URL of the screenshot of the page                                   | str      |
| `links`         | list of collected links                                             | list     |
| `title`         | page title                                                          | str      |

## Supported architectures
- linux/amd64
- linux/arm64

## Status
The project is under active development and may have breaking changes till `v1` is released. However, we are trying our best not to break things unless there is a good reason. As of version `v0.8.0`, Scrapper is considered good enough for real-life usage, and many setups are running it in production.

## License
[Apache-2.0 license](LICENSE)
