from pathlib import Path
import os
import dotenv

from pypresence import *
import time

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_file = os.path.join(BASE_DIR,".env")
def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname)

client_id = token_get('DISCORD_CLIENT_ID')  # Enter your Application ID here.
RPC = Presence(client_id=client_id)
RPC.connect()

RPC.update(
    party_id = "ae488379-351d-4a4f-ad32-2b9b01c91657",
    details = "Minato Namikaze aka Yondaime Hokage. Just invite him.",
    state="Minato Namikaze", 
    large_image="gtvefym", 
    large_text="Minato Namikaze",
    small_image="minato_namikaze", 
    small_text="Yondaime Hokage",
    buttons=[
        {"label": "Invite", "url": "https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=2147483656&scope=bot"}, 
        {"label": "Server", "url": "https://discord.gg/g9zQbjE73K"},
    ]
)

while True:
    time.sleep(15)