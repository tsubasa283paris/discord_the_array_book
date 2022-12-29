#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord

from source.game_controller import GameController
from source.tab_controller import TABController

class GameBox(discord.Client):
    gamech_id: int
    gc: GameController

    async def on_ready(self) -> None:
        print("------------")
        print("Logged in as")
        print(self.user.name)
        print("------------")
        self.gc = GameController()
        self.gc.initialize(self.get_all_members, self.gamech_id)

    async def on_message(self, message: discord.Message) -> None:
        msgs, switch_id = self.gc.on_message(message)
        for msg in msgs:
            await self.send_message(msg[0], msg[1])
        if switch_id != 0:
            if switch_id == 1:
                # tab
                self.gc = TABController()
            self.gc.initialize(self.get_all_members, self.gamech_id)
    
    async def send_message(self, name: str or None, message: str or discord.File)\
                                                                    -> None:
        if name is None:
            await self.get_channel(self.gc.gamech_id).send(message)
        else:
            for member in self.gc.members:
                if member.name == name:
                    dm = await member.create_dm()
                    if type(message) == str:
                        await dm.send(message)
                    elif type(message) == discord.File:
                        await dm.send(file=message)
                    break
    
    def load_channel(self, id: int) -> None:
        self.gamech_id = id
