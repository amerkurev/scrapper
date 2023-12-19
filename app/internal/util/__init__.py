from urllib.parse import parse_qs
from starlette.datastructures import URL


def split_url(url: URL) -> (str, str, dict):
    """
    Split URL into parts. Return host_url, full_path, query_dict.
    :param url: Starlette URL object
    :return:
        host_url - just the host with scheme
        full_path - just the path with query
        query_dict - query params as a dict
    """
    # just the host with scheme
    host_url = URL(scheme=url.scheme, netloc=url.netloc)
    # just the path with query
    full_path = URL(path=url.path, query=url.query)
    # query params as a dict
    query_dict = parse_qs(qs=url.query, keep_blank_values=True)
    return host_url, full_path, query_dict
