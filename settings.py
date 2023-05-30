import os
from os.path import join, dirname

from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("DISCO_TOKEN")
CHID = os.environ.get("DISCO_CHID")
NTN_LO = os.environ.get("NTN_LO")
