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
ntn_layout = settings.NTN_LO
bfs_themes = settings.BFS_TH

if token == "" or channelID == "":
    raise ValueError(".env not set properly")

gamebox.load_channel(int(channelID))
gamebox.set_ntn_lo(ntn_layout)
gamebox.set_bfs_th(bfs_themes)
gamebox.run(token)
