# Scrapper 🧹

If you were looking for a web scraper that actually works, you just found it. It's called Scapper! Downloading a page from the Internet and then extracting an article from it in a structured format is not as easy as it may seem at first glance. Sometimes it can be damn hard. But Scapper will help you with this, I hope :) To do this, Scapper has plenty of features.

Yes, of course, you can use commercial services for your tasks, but Scrapper has been and will always be completely free for you. Scrapper has combined all the power and experience of related Open Source projects, so first, try it out.

<details>
  <summary><b>Quick start</b></summary>

Start a scrapper instance:
```console
docker run -p 3000:3000 --name scrapper amerkurev/scrapper:master
```
Or start with persistent user data and cached files:
```console
docker run -p 3000:3000 -v $(PWD)/user_data_dir:/home/user/user_data_dir --name scrapper amerkurev/scrapper:master
```
Scapper will be available at http://localhost:3000/. For more details, see [Usage](#usage)
</details>


## Demo
(TODO)


## Features
The main features of Scrapper are:
- **The headless browser is already built-in.** Modern websites actively use JavaScript on their pages, fight against crawlers, and sometimes require user actions, such as agreeing to the use of cookies on the site. All of these tasks are solved by the Scrapper using the excellent Playwright project. The Scrapper container image is based on the Playwright image, which already includes all modern browsers.
- **The Read mode in the browser is used for parsing.** Millions of people use the "Read" mode in the browser to display only the text of the article on the screen while hiding the other elements of the page. Scrapper follows the same path by using the excellent Readability.js library from Mozilla. The parsing result will be the same as in the "Read" mode of your favorite browser.
- **A simple and beautiful web interface.** Working with Scrapper is easy and enjoyable because you can do it right in your browser. The simple web interface allows you to debug your query, experiment with each parameter in the API, and see the result in HTML, JSON, or a screenshot. The beautiful design helps achieve an excellent Pico project. A dark theme for comfortable reading is also available.
- **The Scrapper REST API is incredibly simple** to use as it only requires a single call and just a few parameters making it easy to integrate into any project. Furthermore, the web interface offers a visual query-builder that simplifies the learning process for the user.

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
```
docker pull amerkurev/scrapper:latest
```

### Using Scrapper
Scrapper uses two directories on the disk. The first one is the `user_data_dir` directory. This directory contains browser session data such as cookies and local storage. Additionally, the cache of Scrapper's own results (including screenshots) is stored in this directory. The second directory is `user_scripts`. In this directory, you can place your own JavaScript scripts, which you can then embed on pages through the Scrapper API. For example, to remove ads blocks or click the "Accept Cookies" button (see the `user_scripts` parameter in the [API Reference](#api-reference) section for more information). Therefore, it is recommended to immediately mount the corresponding directories from the host and run Scrapper like this:
```
mkdir -p user_data_dir user_scripts

docker run -p 3000:3000 -v $(PWD)/user_data_dir:/home/user/user_data_dir -v $(PWD)/user_scripts:/home/user/user_scripts --name scrapper amerkurev/scrapper:master
```
The Scrapper web interface should now be available at http://localhost:3000/. Use any modern browser to access it.

## API Reference
### GET /parse?url=...
The Scrapper API is very simple. Essentially, it is just one call that can easily be demonstrated using the cURL:

```
curl -X GET "localhost:3000/parse?url=https://en.wikipedia.org/wiki/web_scraping"
```

Use the GET method on the `/parse` endpoint, passing one required parameter `url`. This is the full URL of the webpage on the Internet that contains an article. Scrapper will load the webpage in a browser, extract the article text, and return it in JSON format in the response.

All other request parameters are optional and have default values. However, you can customize them to your liking. The table below lists all the parameters that you can use, along with their descriptions and default values. To make it easier to build requests, use the web interface where the final request link is generated in real-time as you configure the parameters.

### Request Parameters

#### Scrapper settings:
| Parameter                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Default |
|:-------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
| `url`                    | Page URL. The page should contain the text of the article that needs to be extracted.                                                                                                                                                                                                                                                                                                                                                                                    |         |
| `cache`                  | All results of the parsing process will be cached in the user_data_dir directory. Cache can be disabled by setting the cache option to false. In this case, the page will be fetched and parsed every time. Cache is enabled by default.                                                                                                                                                                                                                                 | `true`  |
| `full-content`           | If this option is set to true, the result will have the full HTML contents of the page (fullContent field in the response).                                                                                                                                                                                                                                                                                                                                              | `false` |
| `stealth`                | Stealth mode allows you to bypass anti-scraping techniques. It is disabled by default.                                                                                                                                                                                                                                                                                                                                                                                   | `false` |
| `screenshot`             | If this option is set to true, the result will have the link to the screenshot of the page (screenshot field in the response).                                                                                                                                                                                                                                                                                                                                           | `false` |
| `user-scripts`           | To use your JavaScript scripts on the page, add script files to the "user_scripts" directory, and list the required ones (separated by commas) in the "user-scripts" parameter. These scripts will execute after the page loads but before the article parser runs. This allows you to help parse the article in a variety of ways, such as removing markup, ad blocks, or anything else. For example: `user-scripts=remove_ads.js, click_cookie_accept_button.js`       |         |

#### Playwright settings:
| Parameter                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Default              |
|:-------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------|
| `incognito`              | Allows creating "incognito" browser contexts. "Incognito" browser contexts don't write any browsing data to disk.                                                                                                                                                                                                                                                                                                                                                                                                       | `true`               |
| `timeout`                | Maximum operation time to navigate to the page in milliseconds; defaults to 30000 (30 seconds). Pass 0 to disable the timeout.                                                                                                                                                                                                                                                                                                                                                                                          | `30000`              |
| `wait_until`             | When to consider navigation succeeded, defaults to "domcontentloaded". Events can be either:<br/>- load - consider operation to be finished when the "load" event is fired.<br/>- domcontentloaded - consider operation to be finished when the DOMContentLoaded event is fired.<br/>- networkidle -  consider operation to be finished when there are no network connections for at least 500 ms.<br/>- commit - consider operation to be finished when network response is received and the document started loading. | `domcontentloaded`   |
| `sleep`                  | Waits for the given timeout in milliseconds before parsing the article, and after the page has loaded. In many cases, a sleep timeout is not necessary. However, for some websites, it can be quite useful. Other waiting mechanisms, such as network events or waiting for selector visibility, are not currently supported. The default value is 300 milliseconds.                                                                                                                                                    | `300`                |
| `viewport-width`         | The viewport width in pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | `414`                |
| `viewport-height`        | The viewport height in pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | `896`                |
| `screen-width`           | The page width in pixels. Emulates consistent window screen size available inside web page via window.screen. Is only used when the viewport is set.                                                                                                                                                                                                                                                                                                                                                                    | `828`                |
| `screen-height`          | The page height in pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | `1792`               |
| `ignore-https-errors`    | Whether to ignore HTTPS errors when sending network requests. Defaults to not ignore.                                                                                                                                                                                                                                                                                                                                                                                                                                   | `false`              |
| `user-agent`             | Specific user agent.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                      |
| `locale`                 | Specify user locale, for example en-GB, de-DE, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting rules.                                                                                                                                                                                                                                                                                                                                      |                      |
| `timezone`               | Changes the timezone of the context. See ICU's metaZones.txt for a list of supported timezone IDs.                                                                                                                                                                                                                                                                                                                                                                                                                      |                      |
| `http-credentials`       | Credentials for HTTP authentication (string containing username and password separated by a colon, e.g. "username:password").                                                                                                                                                                                                                                                                                                                                                                                           |                      |
| `extra-http-headers`     | Contains additional HTTP headers to be sent with every request. Example: "X-API-Key:123456;X-Auth-Token:abcdef".                                                                                                                                                                                                                                                                                                                                                                                                        |                      |

#### Network proxy settings:
| Parameter                | Description                                                                                                                                                                                         | Default |
|:-------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
| `proxy-server`           | Proxy to be used for all requests. HTTP and SOCKS proxies are supported, for example http://myproxy.com:3128 or socks5://myproxy.com:3128. Short form myproxy.com:3128 is considered an HTTP proxy. |         |
| `proxy-bypass`           | Optional comma-separated domains to bypass proxy, for example ".com, chromium.org, .domain.com".                                                                                                    |         |
| `proxy-username`         | Optional username to use if HTTP proxy requires authentication.                                                                                                                                     |         |
| `proxy-password`         | Optional password to use if HTTP proxy requires authentication.                                                                                                                                     |         |

#### Readability settings:
| Parameter                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Default |
|:-------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|
| `max-elems-to-parse`     | The maximum number of elements to parse. The default value is 0, which means no limit.                                                                                                                                                                                                                                                                                                                                                                         | 0       |
| `nb-top-candidates`      | The number of top candidates to consider when analysing how tight the competition is among candidates.                                                                                                                                                                                                                                                                                                                                                         | 5       |
| `char-threshold`         | The number of characters an article must have in order to return a result.                                                                                                                                                                                                                                                                                                                                                                                     | 500     |

### Response fields
The response to the `/parse` request returns a JSON object that contains fields, which are described in the table below.

## License
[Apache-2.0](LICENSE)
