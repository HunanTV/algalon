import os

from .openid2_ext import OpenID2

openid2 = OpenID2(file_store_path=os.getenv('NBE_PERMDIR', ''))
