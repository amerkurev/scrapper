
# # # Custom scraper settings:

# Page URL. The page should contain the text of the article that needs to be extracted.
URL = 'url'

# If the option is present, the cache will be ignored.
NO_CACHE = 'noCache'

# If the option is present, the result will have the full HTML contents of the page, including the doctype.
FULL_CONTENT = 'fullContent'


# # # Playwright settings:

# The viewport width in pixels. The default value is 414.
VIEWPORT_WIDTH = 'viewportWidth'

# The viewport height in pixels. The default value is 896.
VIEWPORT_HEIGHT = 'viewportHeight'

# Waits for the given timeout in milliseconds before parsing the article.
# In many cases, a timeout is not necessary. However, for some websites, it can be quite useful, such as with the Bloomberg site
# where it was necessary to set a timeout of up to 10 seconds. Other waiting mechanisms,
# such as network events or waiting for selector visibility, are not currently supported.
# The default value is 300 milliseconds.
WAIT_FOR_TIMEOUT = 'waitForTimeout'


# # # Readability settings:

# The maximum number of elements to parse. The default value is 0, which means no limit.
MAX_ELEMS_TO_PARSE = 'maxElemsToParse'

# The number of top candidates to consider when analysing how tight the competition is among candidates.
# The default value is 5.
NB_TOP_CANDIDATES = 'nbTopCandidates'

# The number of characters an article must have in order to return a result.
# The default value is 500.
CHAR_THRESHOLD = 'charThreshold'
