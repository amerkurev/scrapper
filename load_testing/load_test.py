import argparse
import asyncio
import httpx
import os
import sys
import time

from dataclasses import dataclass
from collections import Counter
from enum import Enum
from http import HTTPStatus


class ParseStatus(str, Enum):
    OK = "OK"  # http code 200
    INVALID_REQUEST = "INVALID_REQUEST"  # http code 422, client error
    ERROR = "ERROR"  # other errors


DEFAULT_CONCUR_REQ = 5
DEFAULT_URLS_FILE = "urls.txt"
DEFAULT_SCRAPPER_HOST = "http://127.0.0.1:3001"


@dataclass
class Options:
    urls_file: str = DEFAULT_URLS_FILE
    scrapper_host: str = DEFAULT_SCRAPPER_HOST
    concur_req: int = DEFAULT_CONCUR_REQ
    verbose: bool = False


async def parse_one_page(
    client: httpx.AsyncClient,
    scrapper_host: str,
    page_url: str,
    semaphore: asyncio.Semaphore,
    verbose: bool,
) -> ParseStatus:
    try:
        host = scrapper_host.rstrip("/")
        url = f"{host}/api/article"
        params = {"url": page_url, "cache": "no"}
        async with semaphore:
            resp = await client.get(url, params=params, timeout=httpx.Timeout(30.0))
            resp.raise_for_status()
            # data = resp.json()
    except httpx.HTTPStatusError as exc:
        if resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            status = ParseStatus.INVALID_REQUEST
            msg = f"[{status}] {page_url}: {exc.response.text}"
        else:
            raise
    else:
        status = ParseStatus.OK
        msg = f"[{status}] {page_url}"

    if verbose and msg:
        print(msg)
    return status


async def supervisor(
    pages: list[str],
    scrapper_host: str,
    concur_req: int,
    verbose: bool,
) -> Counter[ParseStatus]:
    counter: Counter[ParseStatus] = Counter()
    semaphore = asyncio.Semaphore(concur_req)

    async with httpx.AsyncClient() as client:
        to_do = [
            parse_one_page(
                client,
                scrapper_host,
                page_url,
                semaphore,
                verbose,
            )
            for page_url in pages
        ]

        for coro in asyncio.as_completed(to_do):
            error: httpx.HTTPError | None = None
            try:
                status = await coro
            except httpx.HTTPStatusError as exc:
                msg = f"HTTP error {exc.response.status_code}: {exc.response.text}"
                error = exc
            except httpx.RequestError as exc:
                msg = f"Request Error: {type(exc).__name__}"
                error = exc
            except KeyboardInterrupt:
                break

            if error:
                status = ParseStatus.ERROR
                if verbose:
                    page_url = error.request.url.params["url"]
                    print(f"[{status}] {page_url}: {msg}")
            counter[status] += 1

    return counter


def run(
    pages: list[str],
    scrapper_host: str,
    concur_req: int,
    verbose: bool,
) -> Counter[ParseStatus]:
    coro = supervisor(pages, scrapper_host, concur_req, verbose)
    counter = asyncio.run(coro)
    return counter


def process_args() -> Options:
    parser = argparse.ArgumentParser(
        description="Load testing for scrapper. Concurrent parsing of multiple pages.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # show defaults in help
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        type=str,
        default=DEFAULT_URLS_FILE,
        help="file with urls to parse",
    )
    parser.add_argument(
        "-s",
        "--scrapper",
        metavar="HOST",
        type=str,
        default=DEFAULT_SCRAPPER_HOST,
        help="scrapper host",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument(
        "-c",
        "--concur",
        metavar="N",
        type=int,
        default=DEFAULT_CONCUR_REQ,
        help="concurrent requests",
    )
    args = parser.parse_args()

    if os.path.isfile(args.file) is False:
        parser.error(f"File {args.file} not found")
    if (
        args.scrapper.startswith("http://") is False
        and args.scrapper.startswith("https://") is False
    ):
        parser.error(f"Invalid scrapper host {args.scrapper}")
    if args.concur < 1:
        parser.error("Concurrent requests must be > 0")

    return Options(
        urls_file=args.file,
        scrapper_host=args.scrapper,
        concur_req=args.concur,
        verbose=args.verbose,
    )


def get_pages_from_file(filename: str) -> list[str]:
    with open(filename, "r") as f:
        pages = list(filter(None, map(str.strip, f)))
    return pages


def initial_report(pages: list[str], concur_req: int) -> None:
    plural = "s" if len(pages) > 1 else ""
    if concur_req > 1:
        print(
            f"Parsing {len(pages)} page{plural} with {concur_req} concurrent requests."
        )
    else:
        print(f"Parsing {len(pages)} page{plural} one by one (no concurrent requests).")


def final_report(counter: Counter[ParseStatus], start_time: float) -> None:
    elapsed = time.perf_counter() - start_time
    print("-" * 20)
    plural = "s" if counter[ParseStatus.OK] != 1 else ""
    print(f"{counter[ParseStatus.OK]:3} page{plural} parsed.")
    if counter[ParseStatus.INVALID_REQUEST]:
        plural = "s" if counter[ParseStatus.INVALID_REQUEST] != 1 else ""
        print(f"{counter[ParseStatus.INVALID_REQUEST]:3} invalid request{plural}.")
    if counter[ParseStatus.ERROR]:
        plural = "s" if counter[ParseStatus.ERROR] != 1 else ""
        print(f"{counter[ParseStatus.ERROR]:3} error{plural}.")
    print(f"Elapsed time: {elapsed:.2f}s")


def main() -> None:
    opt = process_args()
    pages = get_pages_from_file(opt.urls_file)
    initial_report(pages, opt.concur_req)
    t0 = time.perf_counter()
    counter = run(
        pages=pages,
        scrapper_host=opt.scrapper_host,
        concur_req=opt.concur_req,
        verbose=opt.verbose,
    )
    final_report(counter, t0)
    if counter[ParseStatus.OK] != len(pages):
        sys.exit(1)


if __name__ == "__main__":
    # How to run:
    # python -m load_testing.load_test -f load_testing/urls.txt -c 5 -v
    # or
    # python -m load_test -f urls.txt -c 5 -v (from load_testing directory)
    main()
