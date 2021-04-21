from discord.ext import ipc
from django.conf import settings

class BotIPCConnect:
    def __init__(self):
        if settings.LOCAL:
            self.ipc_client = ipc.Client(
                secret_key=settings.AUTH_PASS,
            )
        else:
            self.ipc_client = ipc.Client(
                    host=settings.HOST,
                    secret_key=settings.AUTH_PASS,
                )
    
    async def get_pfp(self):
        a = await self.ipc_client.request("get_bot_pfp")
        return a
        
        