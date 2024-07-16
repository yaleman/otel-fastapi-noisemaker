import asyncio
import os
import random
import sys
from typing import Callable, Any

import click
import httpcore
from httpx import AsyncClient
from functools import wraps

import httpx

from otel_fastapi_noisemaker import NoiseForm


SERVICE_PORT = int(os.getenv("SERVICE_PORT", "9290"))

DEFAULT_CLIENTS = 10
DEFAULT_METHODS = ["POST", "GET"]
DEFAULT_REQUESTS_PER_CLIENT = 10


def coro(f: Callable[..., Any]) -> Callable[..., Any]:
    """from https://github.com/pallets/click/issues/85, wrap a sync function as asyncio"""

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


URLS = {
    "POST": [
        "/auth/login",
        "/auth/logout",
        "/generate_noise",
    ],
    "GET": [
        "/",
        "/healthcheck",
        "/noise",
    ],
}


@click.command()
@click.option(
    "-c",
    "--client-count",
    default=DEFAULT_CLIENTS,
    help=f"Number of clients to simulate, defaults to {DEFAULT_CLIENTS}",
)
@click.option(
    "-r",
    "--requests",
    help=f"Requests per client, defaults to {DEFAULT_REQUESTS_PER_CLIENT}",
    default=DEFAULT_REQUESTS_PER_CLIENT,
)
@click.option(
    "-m",
    "--methods",
    help=f"Comma-delimited list of HTTP methods to use, defaults to {','.join(DEFAULT_METHODS)}",
    default=",".join(DEFAULT_METHODS),
)
@click.option("-d", "--delay", help="Delay (seconds) between clients", default=0)
@coro
async def main(client_count: int, requests: int, methods: str, delay: int = 0) -> None:
    method_list = methods.split(",")
    for method in method_list:
        if method not in URLS:
            print(f"Invalid method: {method}")
            sys.exit(1)
    base_url = f"http://localhost:{SERVICE_PORT}"
    async with AsyncClient() as client:
        for _ in range(0, client_count):
            # for each client, we generate an IP address and the "Forwarded" header
            my_ip = f"127.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            headers = {
                "Forwarded": f"for={my_ip}",
            }
            # let's do some requestin'
            for _ in range(0, requests):
                method = random.choice(method_list)
                if method == "POST":
                    payload = NoiseForm(message=f"hello from {my_ip}").model_dump()
                else:
                    payload = None

                url = f"{base_url}{random.choice(URLS[method])}"
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        json=payload,
                        headers=headers,
                    )
                    print(f"{my_ip=} {url=} {method=} {response.json()=}")
                except httpcore.ConnectError as error:
                    print(f"Failed to connect:  {url=} {method=} {my_ip=} {error}")
                except httpx.ConnectError as error:
                    print(f"Failed to connect:  {url=} {method=} {my_ip=} {error}")
            if delay > 0:
                print(f"Waiting {delay} second{'' if delay == 1 else 's'}")
                await asyncio.sleep(delay)


if __name__ == "__main__":
    main()
