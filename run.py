#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dotenv import load_dotenv

from source.tab_client import TABClient

tcclient = TABClient()

tcclient.load_channel(channelID)
tcclient.run(token)