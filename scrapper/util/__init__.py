
def check_fields(article, args, fields):
    for (name, types, condition) in fields:
        if condition is None or condition(args):
            assert name in article, f'Missing {name}'
            assert isinstance(article[name], types), f'Invalid {name}'
