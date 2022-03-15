import logging
from typing import Dict, Optional

import aiohttp
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

from .vars import Methods, Tokens

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)

sentry_sdk.init(
    Tokens.sentry_link.value,
    traces_sample_rate=1.0,
    integrations=[
        AioHttpIntegration(),
        ThreadingIntegration(),
        LoggingIntegration(),
        ModulesIntegration(),
    ],
)

async def post_handler(
    method: Methods,
    url: str,
    header: Dict, 
    data: Optional[Dict] = None, 
    json: Optional[Dict] = None,
    log_data: Optional[bool] = False, 
    return_data: Optional[bool] = True, 
    return_json: Optional[bool] = False
):
    header_post = {
        "User-Agent": "Minato Namikaze#6413",
        "X-Ratelimit-Precision": "millisecond",
        'Content-Type' : 'application/json'
    }
    header_post.update(header)
    async with aiohttp.ClientSession() as session:
        async with session.request(method.name, url, headers=header_post, json=data or json) as response:
            data = await response.text()
    if log_data:
        log.info(data)
    if return_data:
        if return_json:
            return data.json()
        return data
