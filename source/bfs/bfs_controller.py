#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from typing import Callable, Dict, List, Tuple, Union

import discord

from source.command import Command
from source.game_controller import GameController, OnMessageResponse, COMMANDS_B, ALWAYS_ALLOWED_COMMANDS_B
from source.bfs.player import PlayerMaster
from source.bfs.best import Best, BestOptions

MAX_CYCLES = 5
ICONS_BF = {
    "MAIN": ":two_women_holding_hands:",
    "CAUT": ":exclamation:",
}
COMMANDS_BF = {
    "SHOWPL": Command("!show_players", "ゲーム参加メンバーリストを表示します。"),
    "JOIN": Command("!join", "ゲーム参加メンバーリストに追加されます。"),
    "LEAVE": Command("!leave", "ゲーム参加メンバーリストから除外されます。"),
    "RESETMMB": Command("!reset_players", "ゲーム参加メンバーリストを全消去します。"),
    "SETCYCLES": Command("!set_cycles", "何周するかを設定します。"),
    "START": Command("!start_game", "ゲームを開始します。"),
    "QUITGM": Command("!quit_game", "ゲームを強制終了します。"),
    "SUBM": Command("!submit", "お題に対する回答を送信します。"),
    "ENDSM": Command("!end_submit", "回答のフェーズを終了し、選択肢開示フェーズに移行します。"),
    "NEXT": Command("!next", "次のターンに移ります。"),
}
PHASES = {
    "S": "standby",
    "R": "reception",
    "A": "answer",
}
ALLOWED_COMMANDS_PER_PHASE_BF = {
    PHASES["S"]: [
        "JOIN",
        "LEAVE",
        "RESETMMB",
        "SETCYCLES",
        "START",
    ],
    PHASES["R"]: [
        "SUBM",
        "ENDSM",
        "QUITGM",
    ],
    PHASES["A"]: [
        "NEXT",
        "QUITGM",
    ],
}
ALWAYS_ALLOWED_COMMANDS_BF = [
    "SHOWPL",
]
ALWAYS_ALLOWED_COMMANDS_BF += ALWAYS_ALLOWED_COMMANDS_B

class BFSController(GameController):
    allowed_commands_per_phase: Dict[str, str]
    commands_dictionary: Dict[str, Command]
    function_dictionary: Dict[str, Callable]
    gamech_id: int
    members: List[discord.Member]
    playermaster: PlayerMaster
    
    phase: str
    best: Best
    best_options: Union[BestOptions, None]

    current_theme: Union[str, None]
    answerer_id_queue: List[int]
    num_cycle: int
    options_all_set_notified: bool

    def __init__(self, th_path: Union[str, None]) -> None:
        super().__init__()
        self.best = Best(th_path)
        self.best_options = None
        self.num_cycle = 1
        self.options_all_set_notified = False

    def initialize(self, get_all_members: Callable, gamech_id: int):
        self.get_all_members = get_all_members
        self.gamech_id = gamech_id
        self.members = [member for member in self.get_all_members()]
        self.playermaster = PlayerMaster()

        self.commands_dictionary = COMMANDS_BF
        self.commands_dictionary.update(COMMANDS_B)

        self.allowed_commands_per_phase = {}
        for p in PHASES.values():
            self.allowed_commands_per_phase[p] = []
            for c in ALLOWED_COMMANDS_PER_PHASE_BF[p] + ALWAYS_ALLOWED_COMMANDS_BF:
                self.allowed_commands_per_phase[p]\
                                .append(self.commands_dictionary[c].get_command())

        self.function_dictionary = {
            self.commands_dictionary["HLP"].get_command(): self.help,
            self.commands_dictionary["SHOWPL"].get_command(): self.show_players,
            self.commands_dictionary["JOIN"].get_command(): self.join,
            self.commands_dictionary["LEAVE"].get_command(): self.leave,
            self.commands_dictionary["RESETMMB"].get_command(): self.reset_players,
            self.commands_dictionary["SETCYCLES"].get_command(): self.set_cycles,
            self.commands_dictionary["START"].get_command(): self.start_game,
            self.commands_dictionary["QUITGM"].get_command(): self.quit_game,
            self.commands_dictionary["SUBM"].get_command(): self.submit,
            self.commands_dictionary["ENDSM"].get_command(): self.end_submit,
            self.commands_dictionary["NEXT"].get_command(): self.next,
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
            ret_mes = f"{ICONS_BF['MAIN']} {author.name}の参加を承りました。"
            return OnMessageResponse([(None, ret_mes)])
    
    def leave(self, _, author: discord.Member) -> OnMessageResponse:
        if self.playermaster.remove_player(author.name):
            ret_mes = f"{ICONS_BF['MAIN']} {author.name}の参加を取り消しました。"
            return OnMessageResponse([(None, ret_mes)])
    
    def reset_players(self, *_) -> OnMessageResponse:
        ret_mes = f"{ICONS_BF['MAIN']} 参加メンバーをリセットしました。"
        self.playermaster.remove_all()
        return OnMessageResponse([(None, ret_mes)])
    
    def set_cycles(self, args_str: str, author: discord.Member) -> OnMessageResponse:
        ok = True
        temp = 0
        try:
            temp = int(args_str)
        except ValueError:
            ok = False
        ok &= 0 < temp <= MAX_CYCLES
        if ok:
            self.num_cycle = temp
            ret_mes = f"{ICONS_BF['MAIN']} 周回数が{temp}に設定されました。"
            ret_mem = None
        else:
            ret_mes = f"{ICONS_BF['CAUT']} 与えられた文字が数字として解釈できないか、"\
                    + f"規定された範囲 1 ≦ n ＜ {MAX_CYCLES}を超えています。"
            ret_mem = author.name
        return OnMessageResponse([(ret_mem, ret_mes)])

    def start_game(self, *_) -> OnMessageResponse:        
        ret: List[Tuple[Union[str, None], str]] = []
        # 共有情報
        ret_mes = f"{ICONS_BF['MAIN']} **ゲームを開始します！**\n" \
                + "参加者一覧：\n"
        for p in self.playermaster.get_players():
            ret_mes += f"- {p.get_name()}\n"
        self.phase = PHASES["R"]
        ret.append((None, ret_mes))

        # 回答者IDのキューを作成
        rand_id_queue = list(range(self.playermaster.len_players()))
        random.shuffle(rand_id_queue)
        self.answerer_id_queue = rand_id_queue * self.num_cycle

        # 全員へ操作方法の通知
        cmd = self.commands_dictionary["SUBM"].get_command()
        for p in self.playermaster.get_players():
            ret_mes = f"{ICONS_BF['MAIN']} `{cmd}` のあとにお題に沿った言葉を半角スペースを空けて打ち込んでください。\n" \
                    + "ゲームマスターが開示フェーズに移行するまでは何度でも上書きできます。\n\n" \
                    + "コマンド例\n" \
                    + "```\n" \
                    + f"{cmd} ルーブル美術館\n" \
                    + "```"
            ret.append((p.get_name(), ret_mes))
        
        # ターン進行処理
        self.current_theme = self.best.get_random_theme()
        self.best_options = BestOptions(self.playermaster.len_players())
        answerer = self.playermaster.get_players()[self.answerer_id_queue[0]]
        self.best_options.set_answerer_id(self.answerer_id_queue[0])
        ret_mes = f"{ICONS_BF['MAIN']} お題：{answerer.get_name()}さんの" \
                + f"「ベスト'{self.current_theme}'」"
        ret.append((None, ret_mes))
        
        return OnMessageResponse(ret)
    
    def quit_game(self, *_) -> OnMessageResponse:
        ret_mes = f"{ICONS_BF['MAIN']} ゲームが強制終了されました。\n" \
                + "（参加メンバーは保存されています。）"
        self.phase = PHASES["S"]
        return OnMessageResponse([(None, ret_mes)])
    
    def submit(self, args_str: str, author: discord.Member) -> OnMessageResponse:
        is_player = False
        player_id = 0
        for i, player in enumerate(self.playermaster.get_players()):
            if player.get_name() == author.name:
                is_player = True
                player_id = i
        
        if not is_player:
            ret_mes = f"{ICONS_BF['CAUT']} ゲームに参加していません！"
            return OnMessageResponse([(author.name, ret_mes)])
    
        if player_id == self.answerer_id_queue[0]:
            ret_mes = f"{ICONS_BF['CAUT']} あなたが回答者です！"
            return OnMessageResponse([(author.name, ret_mes)])
        
        self.best_options.set_option(player_id, args_str)
        
        ret: List[Tuple[Union[str, None], str]] = []

        ret_mes = f"{ICONS_BF['MAIN']} 入力を受け付けました！"
        ret.append((author.name, ret_mes))

        if self.best_options.all_set() and not self.options_all_set_notified:
            # 全員が投稿した段階で通知
            ret_mes = f"{ICONS_BF['MAIN']} すべてのプレイヤーからの投稿が終わりました！"
            self.options_all_set_notified = True
            ret.append((None, ret_mes))
        
        return OnMessageResponse(ret)
    
    def end_submit(self, _, author: discord.Member) -> OnMessageResponse:
        if not self.best_options.all_set():
            ret_mes = f"{ICONS_BF['CAUT']} すべてのプレイヤーからの投稿が完了していません！"
            return OnMessageResponse([(author.name, ret_mes)])
    
        self.phase = PHASES["A"]

        ret: List[Tuple[Union[str, None], str]] = []

        options_str_list = self.best_options.list_random()

        ret_mes = ""
        for i, option in enumerate(options_str_list):
            ret_mes += f"{chr(65 + i)}: {option}\n"
        ret.append((None, ret_mes))

        return OnMessageResponse(ret)
    
    def next(self, *_) -> OnMessageResponse:
        self.options_all_set_notified = False
        
        if len(self.answerer_id_queue) == 1:
            ret_mes = f"{ICONS_BF['CAUT']} ゲーム終了で～す！"
            self.phase = PHASES["S"]
            return OnMessageResponse([(None, ret_mes)])
        
        ret: List[Tuple[Union[str, None], str]] = []


        self.current_theme = self.best.get_random_theme()
        self.best_options = BestOptions(self.playermaster.len_players())

        self.answerer_id_queue = self.answerer_id_queue[1:]

        answerer = self.playermaster.get_players()[self.answerer_id_queue[0]]
        self.best_options.set_answerer_id(self.answerer_id_queue[0])
        ret_mes = f"{ICONS_BF['MAIN']} お題：{answerer.get_name()}さんの" \
                + f"「ベスト'{self.current_theme}'」"
        ret.append((None, ret_mes))

        self.phase = PHASES["R"]

        return OnMessageResponse(ret)
