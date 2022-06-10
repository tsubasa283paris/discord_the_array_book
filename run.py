#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings
from source.tab_client import TABClient

tcclient = TABClient()

token = settings.TOKEN
channelID = settings.CHID

if token == "" or channelID == "":
    raise ValueError(".env not set properly")

tcclient.load_channel(channelID)
tcclient.run(token)