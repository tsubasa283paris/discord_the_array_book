#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import discord

from source.command import Command
from source.game_controller import GameController, COMMANDS_B, ALWAYS_ALLOWED_COMMANDS_B
from source.tab.book import LineBreakForbiddenError
from source.tab.player import PlayerMaster, UnknownPlayerError

MAX_CYCLES = 10
ICONS_T = {
    "MAIN": ":book:",
    "CAUT": ":exclamation:",
}
COMMANDS_T = {
    "SHOWPL": Command("!!show_players", "ゲーム参加メンバーリストを表示します。"),
    "JOIN": Command("!!join", "ゲーム参加メンバーリストに追加されます。"),
    "LEAVE": Command("!!leave", "ゲーム参加メンバーリストから除外されます。"),
    "RESETMMB": Command("!!reset_players", "ゲーム参加メンバーリストを全消去します。"),
    "SETCYCLES": Command("!!set_cycles", "何周するかを設定します。"),
    "START": Command("!!start_game", "ゲームを開始します。"),
    "QUITGM": Command("!!quit_game", "ゲームを強制終了します。"),
    "SETTITLE": Command("!!set_title", "自分の小説のタイトルを設定します。"),
    "STARTSCRPT": Command("!!start_script", "タイトル設定を確定して本文の執筆フェーズに入ります。"),
    "SETSCRPT": Command("!!set_script", "そのターンの本文執筆内容を設定します。すでに設定済みの場合上書きされます。"),
    "NEXT": Command("!!next_turn", "そのターンの本文を確定して、次のターンに移ります。"),
}
PHASES = {
    "S": "standby",
    "GT": "game_title",
    "GS": "game_script",
}
ALLOWED_COMMANDS_PER_PHASE = {
    PHASES["S"]: [
        "JOIN",
        "LEAVE",
        "RESETMMB",
        "SETCYCLES",
        "LNCG",
        "SETCH",
        "RELOADMMB",
        "START",
    ],
    PHASES["GT"]: [
        "QUITGM",
        "SETTITLE",
        "STARTSCRPT",
    ],
    PHASES["GS"]: [
        "QUITGM",
        "SETSCRPT",
        "NEXT",
    ],
}
ALWAYS_ALLOWED_COMMANDS_T = [
    "SHOWPL",
]
ALWAYS_ALLOWED_COMMANDS_T += ALWAYS_ALLOWED_COMMANDS_B

class TABController(GameController):
    allowed_commands_per_phase: dict # of str: str
    commands_dictionary: dict # of str: Command
    function_dictionary: dict # of str: function
    gamech_id: int
    phase: str
    cycles: int
    members: list # of discord.Member
    playermaster: PlayerMaster
    script_page: int

    title_all_set_notified: bool
    script_all_set_notified: bool

    def initialize(self, get_all_members, gamech_id: int):
        self.get_all_members = get_all_members
        self.gamech_id = gamech_id
        self.members = [member for member in self.get_all_members()]
        self.playermaster = PlayerMaster()

        self.commands_dictionary = COMMANDS_T
        self.commands_dictionary.update(COMMANDS_B)

        self.allowed_commands_per_phase = {}
        for p in PHASES.values():
            self.allowed_commands_per_phase[p] = []
            for c in ALLOWED_COMMANDS_PER_PHASE[p] + ALWAYS_ALLOWED_COMMANDS_T:
                self.allowed_commands_per_phase[p]\
                                .append(self.commands_dictionary[c].get_command())

        self.function_dictionary = {
            self.commands_dictionary["HLP"].get_command(): self.help,
            self.commands_dictionary["SHOWPL"].get_command(): self.show_players,
            self.commands_dictionary["JOIN"].get_command(): self.join,
            self.commands_dictionary["LEAVE"].get_command(): self.leave,
            self.commands_dictionary["RESETMMB"].get_command(): self.reset_players,
            self.commands_dictionary["SETCYCLES"].get_command(): self.set_cycles,
            self.commands_dictionary["SETCH"].get_command(): self.set_channel,
            self.commands_dictionary["RELOADMMB"].get_command(): self.reload_member,
            self.commands_dictionary["START"].get_command(): self.start_game,
            self.commands_dictionary["QUITGM"].get_command(): self.quit_game,
            self.commands_dictionary["SETTITLE"].get_command(): self.set_title,
            self.commands_dictionary["STARTSCRPT"].get_command(): self.start_script,
            self.commands_dictionary["SETSCRPT"].get_command(): self.set_script,
            self.commands_dictionary["NEXT"].get_command(): self.next_turn,
        }

        self.phase = PHASES["S"]
        self.cycles = 1

        print("initialization ok")
        
    def help(self, _, author: discord.Member) -> tuple:
        help_str = "\n".join([
            f"{com.get_command()}: {com.get_help()}"\
                                    for com in self.commands_dictionary.values()
        ])
        ret_mes = f"現在のフェーズは「{self.phase}」です。\n" \
                + "```\n" \
                + help_str + "\n" \
                + "```"
        return ((author.name, ret_mes),)
    
    def show_players(self, _, author: discord.Member) -> tuple:
        ret_mes = "```\n" \
                + "ID: 名前\n" \
                + "==========\n" \
                + self.playermaster.display_players() + "\n" \
                + "```"
        return ((author.name, ret_mes),)
    
    def join(self, _, author: discord.Member) -> tuple:
        if self.playermaster.add_player(author.name):
            ret_mes = f"{ICONS_T['MAIN']} {author.name}の参加を承りました。"
            return ((None, ret_mes),)
    
    def leave(self, _, author: discord.Member) -> tuple:
        if self.playermaster.remove_player(author.name):
            ret_mes = f"{ICONS_T['MAIN']} {author.name}の参加を取り消しました。"
            return ((None, ret_mes),)
    
    def reset_players(self, *_) -> tuple:
        ret_mes = f"{ICONS_T['MAIN']} 参加メンバーをリセットしました。"
        self.playermaster.remove_all()
        return ((None, ret_mes),)
    
    def set_cycles(self, content: str, author: discord.Member) -> tuple:
        ok = True
        temp = 0
        try:
            temp = int(content)
        except ValueError:
            ok = False
        ok &= 0 < temp <= MAX_CYCLES
        if ok:
            self.cycles = temp
            ret_mes = f"{ICONS_T['MAIN']} 周回数が{temp}に設定されました。"
            ret_mem = None
        else:
            ret_mes = f"{ICONS_T['CAUT']} 与えられた文字が数字として解釈できないか、"\
                    + f"規定された範囲 1 ≦ n ＜ {MAX_CYCLES}を超えています。"
            ret_mem = author.name
        return ((ret_mem, ret_mes),)

    def start_game(self, *_) -> tuple:
        ret = []
        # 共有情報
        ret_mes = f"{ICONS_T['MAIN']} **ゲームを開始します！**\n" \
                + "ここからは参加者全員の個人チャットにて案内をいたします。\n" \
                + "まずはタイトルの設定から！\n\n" \
                + "参加者一覧：\n"
        for p in self.playermaster.get_players():
            ret_mes += f"- {p.get_name()}\n"
        self.playermaster.setup()
        self.phase = PHASES["GT"]
        self.title_all_set_notified = False
        self.script_all_set_notified = False
        ret.append((None, ret_mes))

        # 全員へタイトル設定の通知
        setttile_cmd = self.commands_dictionary["SETTITLE"].get_command()
        ret_mes = f"{ICONS_T['MAIN']} `{setttile_cmd}` のあとにタイトルを打ち込み、設定してください。\n" \
                + "ゲームマスターが本文執筆フェーズに移行するまでは何度でも上書きできます。\n" \
                + "タイトルを送信する際は改行をしないように気をつけてください！"
        for p in self.playermaster.get_players():
            ret.append((p.get_name(), ret_mes))
        
        return ret
    
    def quit_game(self, *_) -> tuple:
        ret_mes = f"{ICONS_T['MAIN']} ゲームが強制終了されました。\n" \
                + "（参加メンバーは保存されています。）"
        self.phase = PHASES["S"]
        return ((None, ret_mes),)
    
    def set_title(self, content: str, author: discord.Member) -> tuple:
        ret = []
        ret_mes = f"{ICONS_T['MAIN']} タイトルの変更を受け付けました！"
        all_set = False
        try:
            all_set = self.playermaster.set_book_title(author.name, content)
        except LineBreakForbiddenError:
            ret_mes = f"{ICONS_T['CAUT']} 改行を入れないでください！"
        except UnknownPlayerError:
            ret_mes = f"{ICONS_T['CAUT']} ゲームに参加していません！"
        ret.append((author.name, ret_mes))

        if all_set and not self.title_all_set_notified:
            ret_mes = f"{ICONS_T['MAIN']} 参加者全員からのタイトルの設定を受け付けました！"
            self.title_all_set_notified = True
            ret.append((None, ret_mes))
        
        return ret
    
    def start_script(self, _, author: discord.Member) -> tuple:
        if not self.playermaster.titles_are_set():
            ret_mes = f"{ICONS_T['CAUT']} 参加者全員のタイトルの設定が完了していません！"
            return ((author.name, ret_mes),)
        else:
            ret = []
            # 共有情報
            ret_mes = f"{ICONS_T['MAIN']} 本文の執筆に入ります。\n" \
                    + "1ページ目を執筆中……"
            self.script_page = 0
            self.phase = PHASES["GS"]
            ret.append((None, ret_mes))

            # 全員へ本文執筆の通知
            setscrpt_cmd = self.commands_dictionary["SETSCRPT"].get_command()
            for p in self.playermaster.get_players():
                ret_mes = f"{ICONS_T['MAIN']} 本文の執筆に入ります。"\
                        + f"`{setscrpt_cmd}` のあとに本文を打ち込み、設定してください。\n" \
                        + "ゲームマスターが次のページに移行するまでは何度でも上書きできます。\n" \
                        + "また、本文が送信されると文字数を返却します。200～300文字がちょうどよい目安です！\n\n" \
                        + f"それでは、あなたの本「{p.get_book_title()}」の記念すべき1ページ目を書き込んでください。"
                ret.append((p.get_name(), ret_mes))
            
            return ret
    
    def set_script(self, content: str, author: discord.Member) -> tuple:
        ret = []
        ret_mes = f"{ICONS_T['MAIN']} {self.script_page + 1}ページ目の変更を受け付けました！" \
                + f"送信されたページの文字数は{len(content)}文字です。"
        all_set = False
        try:
            all_set = self.playermaster.set_book_script\
                                    (author.name, content, self.script_page)
        except UnknownPlayerError:
            ret_mes = f"{ICONS_T['CAUT']} ゲームに参加していません！"
        ret.append((author.name, ret_mes))

        if all_set and not self.script_all_set_notified:
            ret_mes = f"{ICONS_T['MAIN']} 参加者全員からの{self.script_page + 1}ページ目の本文を受け付けました！"
            self.script_all_set_notified = True
            ret.append((None, ret_mes))
        
        return ret
    
    def next_turn(self, _, author: discord.Member) -> tuple:
        if not self.playermaster.latest_scripts_are_set():
            ret_mes = f"{ICONS_T['CAUT']} 参加者全員の{self.script_page + 1}ページ目の本文の設定が完了していません！"
            return ((author.name, ret_mes),)
        elif self.script_page == self.cycles * self.playermaster.len_players() - 1:
            # 最終ページが終了した場合
            ret = []

            # 保存
            paths = self.playermaster.save_books()

            # 全員へ完成した本文を送付しファイルを削除する
            players = self.playermaster.get_players()
            for i, p in enumerate(players):
                ret.append((p.get_name(), discord.File(paths[i])))
                os.remove(paths[i])

            # 共有情報
            ret_mes = f"{ICONS_T['MAIN']} 全員の本が完成しました！参加者全員の個人チャットに完成した本を送付しました。"
            self.phase = PHASES["S"]
            ret.append((None, ret_mes))

            return ret
        else:
            # 共有情報
            ret = []
            self.script_page += 1
            ret_mes = f"{self.script_page + 1}ページ目を執筆中……"
            self.script_all_set_notified = False
            self.playermaster.turn_page()
            ret.append((None, ret_mes))

            # 全員へ本文執筆の通知
            for p in self.playermaster.get_players():
                target_book_title = self.playermaster.get_target_book_title\
                                                            (p.get_name())
                target_last_script = self.playermaster.get_target_last_script\
                                                            (p.get_name())
                ret_mes = f"{ICONS_T['MAIN']} 本「{target_book_title}」の{self.script_page + 1}ページ目を書き込んでください。\n" \
                        + f"{self.script_page}ページ目の内容は以下の通りでした。\n" \
                        + "```\n" \
                        + f"{target_last_script}\n" \
                        + "```"
                ret.append((p.get_name(), ret_mes))
            
            return ret
