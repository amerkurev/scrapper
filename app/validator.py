
def validate_args(args):
    err = []
    if not args.get('url'):
        err.append('Page URL is required')

    return err
