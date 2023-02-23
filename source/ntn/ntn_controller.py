#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Callable, Dict, List, Tuple, Union

import discord

from source.command import Command
from source.game_controller import GameController, OnMessageResponse, COMMANDS_B, ALWAYS_ALLOWED_COMMANDS_B
from source.ntn.player import PlayerMaster, UnknownPlayerError
from source.ntn.script import Script

ICONS_N = {
    "MAIN": ":newspaper:",
    "CAUT": ":exclamation:",
}
COMMANDS_N = {
    "SHOWPL": Command("!show_players", "ゲーム参加メンバーリストを表示します。"),
    "JOIN": Command("!join", "ゲーム参加メンバーリストに追加されます。"),
    "LEAVE": Command("!leave", "ゲーム参加メンバーリストから除外されます。"),
    "RESETMMB": Command("!reset_players", "ゲーム参加メンバーリストを全消去します。"),
    "START": Command("!start_game", "ゲームを開始します。"),
    "QUITGM": Command("!quit_game", "ゲームを強制終了します。"),
    "FILL": Command("!fill", "空欄を指定の言葉で埋めます。"),
    "ENDFL": Command("!end_fill", "空欄埋めのフェーズを終了し、読み上げフェーズに移行します。"),
    "OPEN": Command("!open", "次の空欄を開けます。"),
}
PHASES = {
    "S": "standby",
    "F": "fill",
    "R": "recite",
}
ALLOWED_COMMANDS_PER_PHASE_N = {
    PHASES["S"]: [
        "JOIN",
        "LEAVE",
        "RESETMMB",
        "LNCG",
        "SETCH",
        "RELOADMMB",
        "START",
    ],
    PHASES["F"]: [
        "QUITGM",
        "FILL",
        "ENDFL",
    ],
    PHASES["R"]: [
        "QUITGM",
        "OPEN",
    ],
}
ALWAYS_ALLOWED_COMMANDS_N = [
    "SHOWPL",
]
ALWAYS_ALLOWED_COMMANDS_N += ALWAYS_ALLOWED_COMMANDS_B

class NTNController(GameController):
    allowed_commands_per_phase: Dict[str, str]
    commands_dictionary: Dict[str, Command]
    function_dictionary: Dict[str, Callable]
    gamech_id: int
    phase: str
    members: List[discord.Member]
    script: Script
    playermaster: PlayerMaster
    next_open_id: int

    def __init__(self, lo_path: Union[str, None]) -> None:
        super().__init__()
        self.script = Script(lo_path)

    def initialize(self, _, gamech_id: int):
        self.gamech_id = gamech_id
        self.members = [member for member in self.get_all_members()]
        self.playermaster = PlayerMaster()

        self.commands_dictionary = COMMANDS_N
        self.commands_dictionary.update(COMMANDS_B)

        self.allowed_commands_per_phase = {}
        for p in PHASES.values():
            self.allowed_commands_per_phase[p] = []
            for c in ALLOWED_COMMANDS_PER_PHASE_N[p] + ALWAYS_ALLOWED_COMMANDS_N:
                self.allowed_commands_per_phase[p]\
                                .append(self.commands_dictionary[c].get_command())

        self.function_dictionary = {
            self.commands_dictionary["HLP"].get_command(): self.help,
            self.commands_dictionary["SHOWPL"].get_command(): self.show_players,
            self.commands_dictionary["JOIN"].get_command(): self.join,
            self.commands_dictionary["LEAVE"].get_command(): self.leave,
            self.commands_dictionary["RESETMMB"].get_command(): self.reset_players,
            self.commands_dictionary["START"].get_command(): self.start_game,
            self.commands_dictionary["QUITGM"].get_command(): self.quit_game,
            self.commands_dictionary["FILL"].get_command(): self.fill,
            self.commands_dictionary["ENDFL"].get_command(): self.end_fill,
            self.commands_dictionary["OPEN"].get_command(): self.open,
        }

        self.phase = PHASES["S"]

        print("initialization ok")
        
    def help(self, _, author: discord.Member) -> OnMessageResponse:
        help_str = "\n".join([
            f"{com.get_command()}: {com.get_help()}"\
                                    for com in self.commands_dictionary.values()
        ])
        ret_mes = f"現在のフェーズは「{self.phase}」です。\n" \
                + "```\n" \
                + help_str + "\n" \
                + "```"
        return OnMessageResponse([(author.name, ret_mes)])
    
    def show_players(self, _, author: discord.Member) -> OnMessageResponse:
        ret_mes = "```\n" \
                + "ID: 名前\n" \
                + "==========\n" \
                + self.playermaster.display_players() + "\n" \
                + "```"
        return OnMessageResponse([(author.name, ret_mes)])
    
    def join(self, _, author: discord.Member) -> OnMessageResponse:
        if self.playermaster.add_player(author.name):
            ret_mes = f"{ICONS_N['MAIN']} {author.name}の参加を承りました。"
            return OnMessageResponse([(None, ret_mes)])
    
    def leave(self, _, author: discord.Member) -> OnMessageResponse:
        if self.playermaster.remove_player(author.name):
            ret_mes = f"{ICONS_N['MAIN']} {author.name}の参加を取り消しました。"
            return OnMessageResponse([(None, ret_mes)])
    
    def reset_players(self, *_) -> OnMessageResponse:
        ret_mes = f"{ICONS_N['MAIN']} 参加メンバーをリセットしました。"
        self.playermaster.remove_all()
        return OnMessageResponse([(None, ret_mes)])

    def start_game(self, args_str: str, author: discord.Member) -> OnMessageResponse:
        script_id: Union[int, None] = None
        tmp = args_str.split(" ")
        if len(tmp) > 0:
            try:
                script_id = int(tmp[0])
            except:
                ret_mes = f"{ICONS_N['CAUT']} 数字を指定してください！"
                return OnMessageResponse([(author.name, ret_mes)])

            if script_id > self.script.num_layout or script_id <= 0:
                ret_mes = f"{ICONS_N['CAUT']} 無効なIDです！\n" \
                        + f"指定可能な最大のIDは{self.script.num_layout - 1}です。"
                return OnMessageResponse([(author.name, ret_mes)])
        
        try:
            self.script.set_layout(script_id)
        except:
            ret_mes = f"{ICONS_N['CAUT']} 何かがおかしいよ"
            return OnMessageResponse([(author.name, ret_mes)])
        
        players = self.playermaster.get_players()
        if len(players) > self.script.num_blank:
            ret_mes = f"{ICONS_N['CAUT']} プレイヤー数が多すぎます！\n" \
                    + f"{self.script.num_blank}人以下にしてください。"
            return OnMessageResponse([(author.name, ret_mes)])

        ret: List[Tuple[Union[str, None], str]] = []
        # 共有情報
        ret_mes = f"{ICONS_N['MAIN']} **ゲームを開始します！**\n" \
                + "ここからは参加者全員の個人チャットにて案内をいたします。\n\n" \
                + "参加者一覧：\n"
        for p in self.playermaster.get_players():
            ret_mes += f"- {p.get_name()}\n"
        ret_mes += "\n" \
                + "今回のニュース原稿はこちらになります。\n" \
                + "```\n" \
                + f"{self.script.show_script_blank()}\n" \
                + "```"
        self.playermaster.setup(self.script.num_blank)
        self.phase = PHASES["F"]
        self.next_open_id = 0
        ret.append((None, ret_mes))

        # 全員へ操作方法の通知
        cmd = self.commands_dictionary["FILL"].get_command()
        for p in self.playermaster.get_players():
            valid_ids = p.get_valid_ids()
            ret_mes = f"{ICONS_N['MAIN']} `{cmd}` のあとに番号と言葉を半角スペースを空けて打ち込み、空欄を埋めてください。\n" \
                    + "（言葉に半角スペースを含む場合はアンダーバー `_` を代わりにお入れください。）\n" \
                    + "ゲームマスターが読み上げフェーズに移行するまでは何度でも上書きできます。\n" \
                    + "あなたが担当する番号は **" + "** と **".join(map(str, valid_ids)) + "** です。\n\n" \
                    + "原稿はこちらです。\n" \
                    + "```\n" \
                    + f"{self.script.show_script_blank()}\n" \
                    + "```\n\n" \
                    + "コマンド例\n" \
                    + "```\n" \
                    + f"{cmd} 3 大きな栗の木\n" \
                    + "```"
            ret.append((p.get_name(), ret_mes))
        
        return OnMessageResponse(ret)
    
    def quit_game(self, *_) -> OnMessageResponse:
        ret_mes = f"{ICONS_N['MAIN']} ゲームが強制終了されました。\n" \
                + "（参加メンバーは保存されています。）"
        self.phase = PHASES["S"]
        return OnMessageResponse([(None, ret_mes)])
    
    def fill(self, args_str: str, author: discord.Member) -> OnMessageResponse:
        args = args_str.split(" ")
        if len(args) != 2:
            ret_mes = f"{ICONS_N['CAUT']} コマンドの指定方法が間違っています！\n\n" \
                    + "コマンド例\n" \
                    + "```\n" \
                    + f"{self.commands_dictionary['FILL'].get_command()} 3 大きな栗の木\n" \
                    + "```"
            return OnMessageResponse([(author.name, ret_mes)])

        blank_id: int = 0
        try:
            blank_id = int(args[0]) - 1
        except:
            ret_mes = f"{ICONS_N['CAUT']} 数字を指定してください！"
            return OnMessageResponse([(author.name, ret_mes)])

        is_player = False
        valid_ids: List[int] = []
        for player in self.playermaster.get_players():
            if player.get_name() == author.name:
                is_player = True
                valid_ids = player.get_valid_ids()
        
        if not is_player:
            ret_mes = f"{ICONS_N['CAUT']} ゲームに参加していません！"
            return OnMessageResponse([(author.name, ret_mes)])

        if not blank_id in valid_ids:
            disp_valid_ids = list(map(str, [i + 1 for i in valid_ids]))
            ret_mes = f"{ICONS_N['CAUT']} 無効な番号です！\n" \
                    + f"指定可能な番号は **" + "** と **".join(disp_valid_ids) + "** です。"
            return OnMessageResponse([(author.name, ret_mes)])
        
        ret: List[Tuple[Union[str, None], str]] = []

        self.script.fill_blank(blank_id, args[1].replace("_", " "))
        open_ids: List[int] = []
        for valid_id in valid_ids:
            if self.script.is_filled(valid_id):
                open_ids.append(valid_id)
        ret_mes = f"{ICONS_N['MAIN']} 入力を受け付けました！\n" \
                + "現在の原稿はこちらです。\n" \
                + "```\n" \
                + f"{self.script.show_script_limit_open(open_ids)}\n" \
                + "```"
        ret.append((author.name, ret_mes))

        if self.script.all_filled():
            # 全員が空欄を埋めた段階で通知
            ret_mes = f"{ICONS_N['MAIN']} すべての空欄の記入が終わりました！"
            ret.append((None, ret_mes))
            
        return OnMessageResponse(ret)
    
    def end_fill(self, _, author: discord.Member) -> OnMessageResponse:
        if not self.script.all_filled():
            ret_mes = f"{ICONS_N['CAUT']} すべての空欄が埋まっていません！"
            return OnMessageResponse([(author.name, ret_mes)])
    
        self.phase = PHASES["R"]

        ret: List[Tuple[Union[str, None], str]] = []

        ret_mes = f"{ICONS_N['MAIN']} 原稿の読み上げに入ります！\n" \
                + "読み上げ担当の方は次のメッセージをご覧ください。"
        ret.append((None, ret_mes))

        ret_mes = "```\n" \
                + f"{self.script.show_script_blank()}\n" \
                + "```"
        ret.append((None, ret_mes))

        return OnMessageResponse(ret, register_editable=1)
    
    def open(self, *_) -> OnMessageResponse:
        open_ids = list(range(len(self.next_open_id + 1)))
        self.next_open_id += 1

        if self.next_open_id == self.script.num_blank:
            self.phase = PHASES["S"]

        ret_mes = "```\n" \
                + f"{self.script.show_script_limit_open(open_ids)}\n" \
                + "```"
        return OnMessageResponse([(None, ret_mes)], edit=True)
