#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord

import settings
from source.tab_client import TABClient

intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.presences = False
tcclient = TABClient(intents=intents)

token = settings.TOKEN
channelID = settings.CHID

if token == "" or channelID == "":
    raise ValueError(".env not set properly")

tcclient.load_channel(channelID)
tcclient.run(token)
