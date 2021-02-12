from flask import Flask, request, make_response
from pathlib import Path
import os
import dotenv
  
app = Flask(__name__) 


BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_file = os.path.join(BASE_DIR, "bot",".env")
def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname)

app.secret_key = token_get('SECRET_KEY')
  
@app.route("/") 
def home_view():
    if request.authorization and request.authorization.username == token_get('DISCORD_CLIENT_ID') and request.authorization.password == token_get('DISCORD_CLIENT_SECRET'):
        return "<h1>You successfully kept the bot alive!!!</h1>"
    return make_response("Could Not Verify!", 401, {"WWW-Authenticate":"Basic Realm=login required"})