#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union

import discord

from source.game_controller import GameController
from source.tab.tab_controller import TABController
from source.aap.aap_controller import AAPController
from source.ntn.ntn_controller import NTNController
from source.bfs.bfs_controller import BFSController

class GameBox(discord.Client):
    gamech_id: int
    gc: GameController
    edit_target_message: Union[discord.Message, None]
    ntn_lo_path: Union[str, None]
    bfs_th_path: Union[str, None]

    async def on_ready(self) -> None:
        print("------------")
        print("Logged in as")
        print(self.user.name)
        print("------------")
        self.gc = GameController()
        self.gc.initialize(self.get_all_members, self.gamech_id)
        self.edit_target_message = None

    async def on_message(self, message: discord.Message) -> None:
        on_message_res = self.gc.on_message(message)
        if on_message_res.edit:
            if self.edit_target_message is not None:
                await self.edit_target_message.edit(
                    content=on_message_res.message_list[0][1]
                )
        else:
            for i, msg in enumerate(on_message_res.message_list):
                await self.send_message(msg[0], msg[1], i == on_message_res.register_editable_i)
        if on_message_res.switch_game is not None:
            if on_message_res.switch_game == 1:
                # tab
                self.gc = TABController()
            elif on_message_res.switch_game == 2:
                # aap
                self.gc = AAPController()
            elif on_message_res.switch_game == 3:
                # ntn
                self.gc = NTNController(self.ntn_lo_path)
            elif on_message_res.switch_game == 4:
                # bfs
                self.gc = BFSController(self.bfs_th_path)
            self.gc.initialize(self.get_all_members, self.gamech_id)
    
    async def send_message(
            self,
            name: Union[str, None],
            message: Union[str, discord.File],
            register_editable: bool,
        ) -> None:
        channel: Union[discord.GroupChannel, discord.DMChannel]
        if name is None:
            channel = self.get_channel(self.gc.gamech_id)
            await channel.send(message)
        else:
            for member in self.gc.members:
                if member.name == name:
                    channel = await member.create_dm()
                    if type(message) == str:
                        await channel.send(message)
                    elif type(message) == discord.File:
                        await channel.send(file=message)
                    break
        if register_editable:
            self.edit_target_message = \
                [message async for message in channel.history(limit=1)][0]
    
    def load_channel(self, id: int) -> None:
        self.gamech_id = id
    
    def set_ntn_lo(self, path: Union[str, None]) -> None:
        self.ntn_lo_path = path

    def set_bfs_th(self, path: Union[str, None]) -> None:
        self.bfs_th_path = path
