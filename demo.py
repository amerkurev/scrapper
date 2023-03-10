import sys

from playwright.sync_api import Playwright, sync_playwright, expect

url = sys.argv[1]


loadReadability = """
async () => {
    return await new Promise((resolve) => {
        try {
            let s = document.createElement("script");
            s.onload = resolve;
            s.onerror = resolve;
            s.setAttribute("src", "https://www.thetechstreetnow.com/static/js/Readability.js");
            document.head.appendChild(s);
        } catch(err) {
            resolve();
        }
    });
}
"""

parseArticle = """
() => {
    if (typeof Readability === 'undefined') {
        return { err: "The Readability library hasn't loaded correctly." };
    }
    try {
        return new Readability(document).parse();
    } catch(err) {
        return { err: "The Readability couldn't parse the document: " + err.toString() };
    }
}
"""


def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=False)  # https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch
    context = browser.new_context(viewport={ 'width': 414, 'height': 896 }, bypass_csp=True)  # https://playwright.dev/python/docs/api/class-browser#browser-new-context
    page = context.new_page()
    page.goto(url)
    page.wait_for_timeout(1000)  # Waits for the given timeout in milliseconds.
    page.evaluate(loadReadability)
    article = page.evaluate(parseArticle)

    if 'textContent' in article:
        print(article['textContent'])  # title, etc
    else:
        print(article)  # error

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
