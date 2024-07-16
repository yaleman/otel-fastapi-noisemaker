import asyncio
import random
from typing import Dict
from fastapi import FastAPI, Request
from opentelemetry import trace
from pydantic import BaseModel


app = FastAPI()


async def rando_sleep() -> None:
    """asyncio-sleeps a random amount of time"""
    await asyncio.sleep(random.randint(1, 10) / 1000)


class NoiseForm(BaseModel):
    message: str


@app.get("/")
async def root(request: Request) -> Dict[str, str]:
    client_port = request.client.port if request.client is not None else -1
    client_address = request.headers.get("Forwarded", "for=unknown").split("=")[-1]
    await rando_sleep()

    # https://opentelemetry.io/docs/specs/semconv/general/attributes/#other-network-attributes
    current_span = trace.get_current_span()
    current_span.set_attribute("client.address", client_address)
    current_span.set_attribute("client.port", client_port)
    return {"message": "Hello World!"}


@app.get("/healthcheck")
async def healthcheck(request: Request) -> Dict[str, str]:
    client_port = request.client.port if request.client is not None else -1
    client_address = request.headers.get("Forwarded", "for=unknown").split("=")[-1]
    await rando_sleep()

    # https://opentelemetry.io/docs/specs/semconv/general/attributes/#other-network-attributes
    current_span = trace.get_current_span()
    current_span.set_attribute("client.address", client_address)
    current_span.set_attribute("client.port", client_port)
    return {"message": "Ok"}


@app.get("/noise")
async def noise(request: Request) -> Dict[str, str]:
    client_port = request.client.port if request.client is not None else -1
    client_address = request.headers.get("Forwarded", "for=unknown").split("=")[-1]

    await rando_sleep()

    # https://opentelemetry.io/docs/specs/semconv/general/attributes/#other-network-attributes
    current_span = trace.get_current_span()
    current_span.set_attribute("client.address", client_address)
    current_span.set_attribute("client.port", client_port)

    return {
        "message": "Noise!",
        "client_address": client_address,
    }


@app.post("/noise")
async def noise_post(request: Request, form: NoiseForm) -> Dict[str, str]:
    client_port = request.client.port if request.client is not None else -1
    client_address = request.headers.get("Forwarded", "for=unknown").split("=")[-1]

    await rando_sleep()

    # https://opentelemetry.io/docs/specs/semconv/general/attributes/#other-network-attributes
    current_span = trace.get_current_span()
    current_span.set_attribute("client.address", client_address)
    current_span.set_attribute("client.port", client_port)
    return {
        "message": "Noise!",
        "your_message": form.message,
        "client_address": client_address,
    }


@app.post("/auth/login")
async def login_post(request: Request, form: NoiseForm) -> Dict[str, str]:
    client_port = request.client.port if request.client is not None else -1
    client_address = request.headers.get("Forwarded", "for=unknown").split("=")[-1]

    await rando_sleep()

    # https://opentelemetry.io/docs/specs/semconv/general/attributes/#other-network-attributes
    current_span = trace.get_current_span()
    current_span.set_attribute("client.address", client_address)
    current_span.set_attribute("client.port", client_port)
    return {
        "message": "Logged in!",
        "your_message": form.message,
        "client_address": client_address,
    }


@app.post("/auth/logout")
async def loginout_post(request: Request, form: NoiseForm) -> Dict[str, str]:
    client_port = request.client.port if request.client is not None else -1
    client_address = request.headers.get("Forwarded", "for=unknown").split("=")[-1]

    await rando_sleep()

    # https://opentelemetry.io/docs/specs/semconv/general/attributes/#other-network-attributes
    current_span = trace.get_current_span()
    current_span.set_attribute("client.address", client_address)
    current_span.set_attribute("client.port", client_port)
    return {
        "message": "Logged Out!",
        "your_message": form.message,
        "client_address": client_address,
    }


@app.post("/generate_noise")
async def generate_noise(request: Request, form: NoiseForm) -> Dict[str, str]:
    client_port = request.client.port if request.client is not None else -1
    client_address = request.headers.get("Forwarded", "for=unknown").split("=")[-1]

    await rando_sleep()

    # https://opentelemetry.io/docs/specs/semconv/general/attributes/#other-network-attributes
    current_span = trace.get_current_span()
    current_span.set_attribute("client.address", client_address)
    current_span.set_attribute("client.port", client_port)
    return {
        "message": "Logged Out!",
        "your_message": form.message,
        "client_address": client_address,
    }
