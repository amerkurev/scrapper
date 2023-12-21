from app.internal.util.htmlutil import levenshtein_similarity


def test_levenshtein_similarity():
    assert levenshtein_similarity('hello', 'hello') == 1.0
    assert levenshtein_similarity('hello', 'world') == 0.19999999999999996
    assert levenshtein_similarity('hello', 'hell') == 0.8
    assert levenshtein_similarity('hello', 'helo') == 0.8
    assert levenshtein_similarity('hello', 'buy') == 0.0

