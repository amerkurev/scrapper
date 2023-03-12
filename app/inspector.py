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

    # traverse the tree
    for elem in tree.find_all():
        if elem.name == 'h1':
            data['hasH1Tag'] = True
        if elem.name == 'h2':
            data['hasH2Tag'] = True
        if elem.name == 'article':
            data['hasArticleTag'] = True

    # remove all elements before the first h1 or h2 tag
    if data['hasH1Tag'] or data['hasH2Tag']:
        for elem in tree.find_all(text=True):
            if elem.parent.name in ('h1', 'h2'):
                break
            text = elem.text.strip()
            if text:
                p = parent_with_same_text(elem, text=text)
                p.extract()
    data['content'] = str(tree)
    return data


def parent_with_same_text(elem, text):
    if elem.parent and text == elem.parent.text.strip():
        return parent_with_same_text(elem=elem.parent, text=text)
    return elem
