import asyncio
import os
import random
import sys
from typing import Callable, Any, Dict, Optional

import backoff
import click
import httpcore
from httpx import AsyncClient, Response
from functools import wraps
from loguru import logger
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


@backoff.on_exception(
    backoff.expo, [httpcore.ConnectError, httpx.ConnectError], max_tries=10
)
async def get_url(
    client: AsyncClient,
    url: str,
    headers: Dict[str, str],
    json: Optional[Dict[str, Any]] = None,
    method: str = "GET",
) -> Response:
    return await client.request(method=method, url=url, headers=headers, json=json)


async def client_task(
    client_number: int,
    requests: int,
    request_delay: float,
    method_list: list[str],
    base_url: str,
) -> None:
    my_ip = (
        f"127.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    )
    headers = {
        "Forwarded": f"for={my_ip}",
    }

    async with AsyncClient() as client:
        for _ in range(requests):
            method = random.choice(method_list)
            if method == "POST":
                payload = NoiseForm(message=f"hello from {my_ip}").model_dump()
            else:
                payload = None

            url = f"{base_url}{random.choice(URLS[method])}"
            # try:
            response = await get_url(
                client=client,
                method=method,
                url=url,
                json=payload,
                headers=headers,
            )
            logger.debug(f"{my_ip=} {url=} {method=} {response.json()=}")
            # except (httpcore.ConnectError, httpx.ConnectError) as error:
            #     logger.error(f"Failed to connect: {url=} {method=} {my_ip=} {error}")
            #     return
            if request_delay > 0.0:
                await asyncio.sleep(request_delay)
    logger.success("Client {} done!", client_number)


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
@click.option("-d", "--delay", help="Delay (seconds) between clients", default=0.0)
@click.option(
    "-D", "--request-delay", help="Delay (seconds) between requests", default=0.0
)
@click.option("--debug", is_flag=True, help="Enable debug logging")
@coro
async def main(
    client_count: int,
    requests: int,
    methods: str,
    delay: float = 0.0,
    request_delay: float = 0.0,
    debug: bool = False,
) -> None:

    if not debug:
        logger.remove()
        logger.add(sys.stdout, level="INFO")

    method_list = methods.split(",")
    for method in method_list:
        if method not in URLS:
            logger.error(f"Invalid method: {method}")
            sys.exit(1)
    base_url = f"http://localhost:{SERVICE_PORT}"

    tasks = []
    for client_num in range(client_count):
        logger.info(f"Creating client {client_num+1}")
        task = asyncio.create_task(
            client_task(client_num, requests, request_delay, method_list, base_url)
        )
        tasks.append(task)
        if delay > 0:
            logger.debug(f"Waiting {delay} second{'' if delay == 1 else 's'}")
            await asyncio.sleep(delay)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    main()
