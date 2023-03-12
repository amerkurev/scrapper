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

    # 2. remove all p and div tags that contain one word or less (or only digits),
    # and not contain any images (or headers)
    for el in tree.find_all(['p', 'div']):
        # skip if the element has any images (or headers)
        if el.find(['img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            continue
        text = el.get_text(strip=True)
        # remove the element if it contains one word or less (or only digits)
        words = text.split()
        if len(words) <= 1 or (''.join(words)).isnumeric():
            el.decompose()

    data['content'] = str(tree)
    return data
