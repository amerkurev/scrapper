// TODO: this should be python
const override = {
    userAgent:
        this.opts.userAgent ||
        (await page.browser().userAgent()).replace(
            'HeadlessChrome/',
            'Chrome/'
        ),
    acceptLanguage: this.opts.locale || 'en-US,en',
    platform: this.opts.platform || 'Win32'
}

console.log('onPageCreated - Will set these user agent options', {
    override,
    opts: this.opts
})

page._client.send('Network.setUserAgentOverride', override)