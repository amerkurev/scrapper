
from bs4 import BeautifulSoup


header_max_distance = 300
acceptable_link_text_len = 40


def improve_content(data):
    content = data['content']
    tree = BeautifulSoup(content, 'html.parser')

    # 1. remove all p and div tags that contain one word or less (or only digits),
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

    # 2. move the first tag h1 (or h2) to the top of the tree
    title = data['title']
    header_distance = 0

    for el in tree.find_all(text=True):
        # stop if the header is found
        if el.parent.name in ('h1', 'h2'):
            title = el.parent.get_text(strip=True)
            el.parent.decompose()  # 'real' move will be below, at 3.1 or 3.2
            break

        # stop if distance is too big
        header_distance += len(el.text)
        if header_distance > header_max_distance:
            # will be used data['title'] as title
            break

    # 3.1 check if article tag already exists, and then insert the title into it
    for el in tree.find_all():
        if el.name == 'article':
            el.insert(0, BeautifulSoup(f'<h1>{title}</h1>', 'html.parser'))
            return str(tree)

    # 3.2 if not, create a new article tag and insert the title into it
    content = str(tree)
    return f'<article><h1>{title}</h1>{content}</article>'


def improve_link(link):
    lines = link['text'].splitlines()
    text = ''
    # find the longest line
    for line in lines:
        if len(line) > len(text):
            text = line
        # stop if the line is long enough
        if len(text) > acceptable_link_text_len:
            break

    link['text'] = text
    return link
