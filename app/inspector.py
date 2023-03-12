from bs4 import BeautifulSoup


def inspect_content(data):
    title = data['title']
    content = data['content']
    text_content = data['textContent']
    data['titleInContent'] = title in text_content
    data['hasH1Tag'] = False
    data['hasH2Tag'] = False
    data['hasArticleTag'] = False

    tree = BeautifulSoup(content, 'html.parser')

    # 1. traverse the tree and find the h1, h2 and article tags
    for el in tree.find_all():
        if el.name == 'h1':
            data['hasH1Tag'] = True
        if el.name == 'h2':
            data['hasH2Tag'] = True
        if el.name == 'article':
            data['hasArticleTag'] = True

    # 2. remove all text before the first h1 or h2 tag
    if data['hasH1Tag'] or data['hasH2Tag']:
        for el in tree.find_all(text=True):
            if el.parent.name in ('h1', 'h2'):
                break
            text = el.get_text(strip=True)
            if text:
                p = parent_with_same_text(el, text=text)
                p.extract()

    data['content'] = str(tree)
    return data


def parent_with_same_text(el, text):
    if el.parent and text == el.parent.get_text(strip=True):
        return parent_with_same_text(el.parent, text=text)
    return el
