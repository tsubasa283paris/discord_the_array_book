#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Tuple, Union

import discord

from source.command import Command

ICONS_B = {
    "MAIN": ":book:",
    "CAUT": ":exclamation:",
}
COMMANDS_B = {
    "HLP": Command("!help", "今見ているこの画面を表示します。"),
    "HLPG": Command("!help_game", "各ゲームの概要を説明します。"),
    "LNCG": Command("!launch_game", "ゲームを起動します。現在起動中のゲームの情報は破棄されます。"),
    "SETCH": Command("!set_channel", "全体公開メッセージを投稿するチャンネルIDを設定します。"),
    "RELOADMMB": Command("!reload_member", "当botから見えるアカウント一覧を再読み込みします。"),
}
ALWAYS_ALLOWED_COMMANDS_B = [
    "HLP",
    "HLPG",
]

class OnMessageResponse:
    message_list: List[Tuple[Union[str, None], Union[str, discord.File]]]
    switch_game: Union[int, None]
    register_editable_i: Union[int, None]
    edit: bool
    
    def __init__(
            self,
            message_list: List[Tuple[Union[str, None], Union[str, discord.File]]],
            switch_game: Union[int, None] = None,
            register_editable: Union[int, None] = None,
            edit: bool = False,
        ) -> None:
        self.message_list = message_list
        self.switch_game = switch_game
        self.register_editable_i = register_editable
        self.edit = edit

class GameController:
    commands_dictionary: dict # of str: Command
    function_dictionary: dict # of str: function
    gamech_id: int
    members: list

    # function to be called on initialization
    def initialize(self, get_all_members, gamech_id: int):
        self.get_all_members = get_all_members
        self.gamech_id = gamech_id
        self.members = [member for member in self.get_all_members()]

        self.commands_dictionary = COMMANDS_B
        self.function_dictionary = {
            self.commands_dictionary["HLP"].get_command(): self.help,
            self.commands_dictionary["HLPG"].get_command(): self.help_game,
            self.commands_dictionary["SETCH"].get_command(): self.set_channel,
            self.commands_dictionary["RELOADMMB"].get_command(): self.reload_member,
        }

        print("initialization ok")

    # function to be called on receiving message.
    def on_message(self, message: discord.Message) -> OnMessageResponse:
        sep = message.content.split(" ")
        author = message.author

        if sep[0] == self.commands_dictionary["LNCG"].get_command():
            return self.launch_game(" ".join(sep[1:]), author)
        elif sep[0] in self.function_dictionary.keys():
            return self.function_dictionary[sep[0]]\
                        (" ".join(sep[1:]), author)
        
        return OnMessageResponse([])

    def help(self, _, author: discord.Member) -> OnMessageResponse:
        help_str = "\n".join([
            f"{com.get_command()}: {com.get_help()}"\
                                    for com in self.commands_dictionary.values()
        ])
        ret_mes = "```\n" \
                + help_str + "\n" \
                + "```"
        return OnMessageResponse([(author.name, ret_mes)])

    def help_game(self, content: str, author: discord.Member) -> OnMessageResponse:
        ok = True
        temp = 0
        try:
            temp = int(content)
        except ValueError:
            ok = False
        ret_mes = f"{ICONS_B['CAUT']} 与えられた文字が規定されていない数字です。"
        if temp == 0 or not ok:
            ret_mes = f"{ICONS_B['CAUT']} 与えられた文字が数字として解釈できません。"
        elif temp == 1:
            # tab
            ret_mes = "__**TAB**__\n" \
                    + "直前の人の書いたページしか読めないリレー小説です。\n" \
                    + "設定によりますが、多くの場合1ゲームに2時間以上かかります。"
        elif temp == 2:
            # aap
            ret_mes = "__**AAP**__\n" \
                    + "各プレイヤーが1文字ずつ追加して詩を作成するゲームです。\n" \
                    + "設定によりますが、多くの場合1ゲームは30分ほどで終わります。"
        elif temp == 3:
            # ntn
            ret_mes = "__**NTN**__\n" \
                    + "各プレイヤーがニュース原稿の空欄を埋め、一人が読み上げるゲームです。\n" \
                    + "設定によりますが、多くの場合1ゲームは15分ほどで終わります。"
        elif temp == 4:
            # bfs
            ret_mes = "__**BFS**__\n" \
                    + "回答者にとって最も〇〇な回答をしたプレイヤーに得点が入っていくゲームです。\n" \
                    + "設定によりますが、多くの場合1ゲームは15分ほどで終わります。"
        return OnMessageResponse([(author.name, ret_mes)])
    
    def launch_game(self, content: str, author: discord.Member) -> OnMessageResponse:
        ok = True
        temp = None
        try:
            temp = int(content)
        except ValueError:
            ok = False
        ret_mem = author.name
        ret_mes = f"{ICONS_B['CAUT']} 与えられた文字が規定されていない数字です。"
        switch_id = 0
        if temp is None or not ok:
            ret_mes = f"{ICONS_B['CAUT']} 与えられた文字が数字として解釈できません。"
        elif temp == 1:
            # tab
            ret_mem = None
            switch_id = 1
            ret_mes = f"{ICONS_B['MAIN']} ゲームをTABに設定しました。\n" \
                    + "これまで進行していたゲームは破棄されます。"
        elif temp == 2:
            # aap
            ret_mem = None
            switch_id = 2
            ret_mes = f"{ICONS_B['MAIN']} ゲームをAAPに設定しました。\n" \
                    + "これまで進行していたゲームは破棄されます。"
        elif temp == 3:
            # ntn
            ret_mem = None
            switch_id = 3
            ret_mes = f"{ICONS_B['MAIN']} ゲームをNTNに設定しました。\n" \
                    + "これまで進行していたゲームは破棄されます。"
        elif temp == 4:
            # ntn
            ret_mem = None
            switch_id = 4
            ret_mes = f"{ICONS_B['MAIN']} ゲームをBFSに設定しました。\n" \
                    + "これまで進行していたゲームは破棄されます。"
        return OnMessageResponse([(ret_mem, ret_mes)], switch_id)
    
    def set_channel(self, content: str, author: discord.Member) -> OnMessageResponse:
        ok = True
        temp = self.gamech_id
        try:
            temp = int(content)
        except ValueError:
            ok = False
        if ok:
            self.gamech_id = temp
            ret_mes = f"{ICONS_B['MAIN']} 全体公開メッセージ送信チャンネルが当チャンネルに設定されました。"
            ret_mem = None
        else:
            ret_mes = f"{ICONS_B['CAUT']} 与えられた文字が数字として解釈できません。"
            ret_mem = author.name
        return OnMessageResponse([(ret_mem, ret_mes)])
    
    def reload_member(self, _, author: discord.Member) -> OnMessageResponse:
        ret_mes = f"{ICONS_B['MAIN']} 参加しているサーバからアカウント一覧を読み込み直しました。"
        self.members = [member for member in self.get_all_members()]
        return OnMessageResponse([(author.name, ret_mes)])
