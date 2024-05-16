from typing import Union
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from price_trendyol import TrendyolShop
from fastapi.middleware.cors import CORSMiddleware

import asyncio

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trenyol = TrendyolShop()

prev_rate = 0


async def get_rate():
    global prev_rate
    while True:
        try:
            new_rate = trenyol.exchange_rates()
            if prev_rate != new_rate:
                prev_rate = new_rate
                yield prev_rate

            await asyncio.sleep(600)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)


@app.get("/rate")
async def read_root():
    return EventSourceResponse(get_rate())


@app.get("/price/{url:path}")
async def read_root(url: str, merchantId: str | None = None, boutiqueId: str | None = None, v: str | None = None):

    current_url = f'{url}?merchantId=${merchantId}&boutiqueId={boutiqueId}&v={v}'
    if url:
        data = await trenyol.run(current_url, prev_rate)
        if data:
            return data
        else:
            return 'url is fuck!?'

