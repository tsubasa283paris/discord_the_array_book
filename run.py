#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord

import settings
from source.game_box import GameBox

intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.presences = False
gamebox = GameBox(intents=intents)

token = settings.TOKEN
channelID = settings.CHID

if token == "" or channelID == "":
    raise ValueError(".env not set properly")

gamebox.load_channel(int(channelID))
gamebox.run(token)
