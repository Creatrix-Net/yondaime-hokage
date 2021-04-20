import os
import secrets
from random import randint

__doc__ = '''
This module is used to generate the secret key for the this django project,
And safely store it the environment so that it remains safe from hackers and can be also be
uploaded to the source control (like Git) without any tension of losing secret key to the hackers.
Thus it also protects your site cryptographic signin.

import os
Use import AyQ223M.wKe0FHLcxHxw.aZZ34Jb5jXNDQQ.QUircLIAJLBA6EUVYoyawNMcDSo.ALI3g returns the secret key using the os.environ['SECRET_KEY_FOR_SITE']
or you could also use,

from AyQ223M.wKe0FHLcxHxw.aZZ34Jb5jXNDQQ.QUircLIAJLBA6EUVYoyawNMcDSo.ALI3g import dWdhXiCeNK0

or

from AyQ223M.wKe0FHLcxHxw.aZZ34Jb5jXNDQQ.QUircLIAJLBA6EUVYoyawNMcDSo.ALI3g import dWdhXiCeNK0 as s

The secret key are stored in a file in binary format
Thus cannot be decrypted using this module.
And it always get changed when you reload the app i.e. different for development server and production server

eg code,
from AyQ223M.wKe0FHLcxHxw.aZZ34Jb5jXNDQQ.QUircLIAJLBA6EUVYoyawNMcDSo.ALI3g import dWdhXiCeNK0 as s
classindentifier = s()
SECRET_KEY = classindentifier.get_secret_key(appname_in_quotes, classindentifier.salt)  # The Secrect Key
'''

class dWdhXiCeNK0:
    url = str(secrets.token_urlsafe(10000))
    hexvar = str(secrets.token_hex(10000))
    join_url_hexvar = url+hexvar

    def __init__(self, *args, **kwargs):
        self.url = str(secrets.token_urlsafe(10000))
        self.hexvar = str(secrets.token_hex(10000))
        
        self.salt = str(secrets.token_urlsafe(randint(10, 30)))
        
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    
    def gen_secret_key(self, salt):
        '''It generates the secrets key and writes it into file in binary'''
        secret_key = str(self.url+self.hexvar).join(self.salt)
        if len(secret_key) > 32767:
            secret_key = secret_key[:3276]
        
        os.environ.setdefault('SECRET_KEY', secret_key)
    
    
    def get_secret_key(self, salt):
        '''It return the secret key to the user'''
        self.gen_secret_key(self.salt)
        return os.environ['SECRET_KEY'] 