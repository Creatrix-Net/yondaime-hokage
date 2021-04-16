from django.utils.timezone import now
from discord.ext import ipc
from django.conf import settings
from datetime import time


class BotIPCConnect:
    def __init__(self):
        if settings.LOCAL:
            self.host = 'localhost'
        
            self.ipc_client = ipc.Client(
                host=self.host,
                secret_key=settings.AUTH_PASS,
            )
        else:
            self.ipc_client = ipc.Client(
                    secret_key=settings.AUTH_PASS,
                )
    
    async def get_pfp(self):
        a = await self.ipc_client.request("get_bot_pfp")
        return a
        
        