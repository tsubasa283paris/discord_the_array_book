#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

import discord

from source.command import Command
from source.book import LineBreakForbiddenError
from source.player import Player, PlayerMaster, UnknownPlayerError

ICON = ":book:"
CAUT = ":exclamation:"
MAX_CYCLES = 10
COMMANDS = {
    "HLP": Command("!help", "今見ているこの画面を表示します。"),
    "SHOWPL": Command("!show_players", "ゲーム参加メンバーリストを表示します。"),
    "JOIN": Command("!join", "ゲーム参加メンバーリストに追加されます。"),
    "LEAVE": Command("!leave", "ゲーム参加メンバーリストから除外されます。"),
    "RESETMMB": Command("!reset_players", "ゲーム参加メンバーリストを全消去します。"),
    "SETCYCLES": Command("!set_cycles", "何周するかを設定します。"),
    "SETCH": Command("!set_channel", "全体公開メッセージを投稿するチャンネルIDを設定します。"),
    "START": Command("!start_game", "ゲームを開始します。"),
    "QUITGM": Command("!quit_game", "ゲームを強制終了します。"),
    "SETTITLE": Command("!set_title", "自分の小説のタイトルを設定します。"),
    "STARTSCRPT": Command("!start_script", "タイトル設定を確定して本文の執筆フェーズに入ります。"),
    "SETSCRPT": Command("!set_script", "そのターンの本文執筆内容を設定します。すでに設定済みの場合上書きされます。"),
    "NEXT": Command("!next_turn", "そのターンの本文を確定して、次のターンに移ります。"),
}
COMMAND_LIST = [c.get_command() for c in COMMANDS.values()]
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
        "SETCH",
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
ALWAYS_ALLOWED_COMMANDS = [
    "HLP",
    "SHOWPL",
]

class TABClient(discord.Client):
    allowed_commands_per_phase: dict # of str: str
    function_dictionary: dict # of str: function
    gamech_id: int
    phase: str
    cycles: int
    members: list # of discord.Member
    playermaster: PlayerMaster
    script_page: int

    title_all_set_notified: bool
    script_all_set_notified: bool

    async def on_ready(self) -> None:
        print("------------")
        print("Logged in as")
        print(self.user.name)
        print("------------")
        self.initialize()

    async def on_message(self, message: discord.Message) -> None:
        sep = message.content.split(" ")
        author = message.author

        try:
            if sep[0] in self.allowed_commands_per_phase[self.phase]:
                gen = self.function_dictionary[sep[0]]\
                            (" ".join(sep[1:]), author)
                if gen:
                    for mem, mes in gen:
                        await self.send_message(mem, mes)
            elif sep[0] in COMMAND_LIST:
                ret_mes = f"{CAUT} そのコマンドを実行できるフェーズではありません！"
                await self.send_message(author.name, ret_mes)
        except KeyError:
            pass
    
    async def send_message(self, name: str or None, message: discord.Message)\
                                                                    -> None:
        if name is None:
            await self.get_channel(self.gamech_id).send(message)
        else:
            for member in self.members:
                if member.name == name:
                    dm = await member.create_dm()
                    await dm.send(message)
                    break
        
    def help(self, _, author: discord.Member) -> tuple:
        help_str = "\n".join([
            f"{com.get_command()}: {com.get_help()}"\
                                    for com in COMMANDS.values()
        ])
        ret_mes = f"現在のフェーズは「{self.phase}」です。\n" \
                + "```\n" \
                + help_str + "\n" \
                + "```"
        yield author.name, ret_mes
    
    def show_players(self, _, author: discord.Member) -> tuple:
        ret_mes = "```\n" \
                + "ID: 名前\n" \
                + "==========\n" \
                + self.playermaster.display_players() + "\n" \
                + "```"
        yield author.name, ret_mes
    
    def join(self, _, author: discord.Member) -> tuple:
        if self.playermaster.add_player(author.name):
            ret_mes = f"{ICON} {author.name}の参加を承りました。"
            yield None, ret_mes
    
    def leave(self, _, author: discord.Member) -> tuple:
        if self.playermaster.remove_player(author.name):
            ret_mes = f"{ICON} {author.name}の参加を取り消しました。"
            yield None, ret_mes
    
    def reset_players(self, *_) -> tuple:
        ret_mes = f"{ICON} 参加メンバーをリセットしました。"
        self.playermaster.remove_all()
        yield None, ret_mes
    
    def set_cycles(self, content: str, author: discord.Member) -> tuple:
        ok = True
        temp = 0
        try:
            temp = int(content)
        except ValueError:
            ok = False
        ok &= temp <= MAX_CYCLES
        if ok:
            self.cycles = temp
            ret_mes = f"{ICON} 周回数が{temp}に設定されました。"
            ret_mem = None
        else:
            ret_mes = f"{CAUT} 与えられた文字が数字として解釈できないか、"\
                    + f"規定された最大値{MAX_CYCLES}を超えています。"
            ret_mem = author.name
        yield ret_mem, ret_mes
    
    def set_channel(self, content: str, author: discord.Member) -> tuple:
        ok = True
        temp = self.gamech_id
        try:
            temp = int(content)
        except ValueError:
            ok = False
        if ok:
            self.gamech_id = temp
            ret_mes = f"{ICON} 全体公開メッセージ送信チャンネルが当チャンネルに設定されました。"
            ret_mem = None
        else:
            ret_mes = f"{CAUT} 与えられた文字が数字として解釈できません。"
            ret_mem = author.name
        yield ret_mem, ret_mes

    def start_game(self, *_) -> tuple:
        # 共有情報
        ret_mes = f"{ICON} **ゲームを開始します！**\n" \
                + "ここからは参加者全員の個人チャットにて案内をいたします。\n" \
                + "まずはタイトルの設定から！\n\n" \
                + "参加者一覧：\n"
        for p in self.playermaster.get_players():
            ret_mes += f"- {p.get_name()}\n"
        self.playermaster.setup()
        self.phase = PHASES["GT"]
        self.title_all_set_notified = False
        self.script_all_set_notified = False
        yield None, ret_mes

        # 全員へタイトル設定の通知
        setttile_cmd = COMMANDS["SETTITLE"].get_command()
        ret_mes = f"{ICON} `{setttile_cmd}` のあとにタイトルを打ち込み、設定してください。\n" \
                + "ゲームマスターが本文執筆フェーズに移行するまでは何度でも上書きできます。\n" \
                + "タイトルを送信する際は改行をしないように気をつけてください！"
        for p in self.playermaster.get_players():
            yield p.get_name(), ret_mes
    
    def quit_game(self, *_) -> tuple:
        ret_mes = f"{ICON} ゲームが強制終了されました。\n" \
                + "（参加メンバーは保存されています。）"
        self.phase = PHASES["S"]
        yield None, ret_mes
    
    def set_title(self, content: str, author: discord.Member) -> tuple:
        ret_mes = f"{ICON} タイトルの変更を受け付けました！"
        all_set = False
        try:
            all_set = self.playermaster.set_book_title(author.name, content)
        except LineBreakForbiddenError:
            ret_mes = f"{CAUT} 改行を入れないでください！"
        except UnknownPlayerError:
            ret_mes = f"{CAUT} ゲームに参加していません！"
        yield author.name, ret_mes

        if all_set and not self.title_all_set_notified:
            ret_mes = f"{ICON} 参加者全員からのタイトルの設定を受け付けました！"
            self.title_all_set_notified = True
            yield None, ret_mes
    
    def start_script(self, _, author: discord.Member) -> tuple:
        if not self.playermaster.titles_are_set():
            ret_mes = f"{CAUT} 参加者全員のタイトルの設定が完了していません！"
            yield author.name, ret_mes
        else:
            # 共有情報
            ret_mes = f"{ICON} 本文の執筆に入ります。\n" \
                    + "1ページ目を執筆中……"
            self.script_page = 0
            self.phase = PHASES["GS"]
            yield None, ret_mes

            # 全員へ本文執筆の通知
            setscrpt_cmd = COMMANDS["SETSCRPT"].get_command()
            for p in self.playermaster.get_players():
                ret_mes = f"{ICON} 本文の執筆に入ります。"\
                        + f"`{setscrpt_cmd}` のあとに本文を打ち込み、設定してください。\n" \
                        + "ゲームマスターが次のページに移行するまでは何度でも上書きできます。\n" \
                        + "また、本文が送信されると文字数を返却します。200～300文字がちょうどよい目安です！\n\n" \
                        + f"それでは、あなたの本「{p.get_book_title()}」の記念すべき1ページ目を書き込んでください。"
                yield p.get_name(), ret_mes
    
    def set_script(self, content: str, author: discord.Member) -> tuple:
        ret_mes = f"{ICON} {self.script_page + 1}ページ目の変更を受け付けました！" \
                + f"送信されたページの文字数は{len(content)}文字です。"
        all_set = False
        try:
            all_set = self.playermaster.set_book_script\
                                    (author.name, content, self.script_page)
        except UnknownPlayerError:
            ret_mes = f"{CAUT} ゲームに参加していません！"
        yield author.name, ret_mes

        if all_set and not self.script_all_set_notified:
            ret_mes = f"{ICON} 参加者全員からの{self.script_page + 1}ページ目の本文を受け付けました！"
            self.script_all_set_notified = True
            yield None, ret_mes
    
    def next_turn(self, _, author: discord.Member) -> tuple:
        if not self.playermaster.latest_scripts_are_set():
            ret_mes = f"{CAUT} 参加者全員の{self.script_page + 1}ページ目の本文の設定が完了していません！"
            yield author.name, ret_mes
        elif self.script_page == self.cycles * self.playermaster.len_players() - 1:
            # 最終ページが終了した場合
            # 共有情報
            ret_mes = f"{ICON} 全員の本が完成しました！参加者全員の個人チャットに完成した本を送付しました。"
            self.phase = PHASES["S"]
            yield None, ret_mes

            # 全員へ完成した本文を送付
            for p in self.playermaster.get_players():
                book = self.playermaster.get_book(p.get_name())
                ret_mes = f"{ICON} 「{book[0]}」\n"
                for i in range(len(book) - 1):
                    ret_mes += f"{i + 1}.\n" \
                            + "```\n" \
                            + f"{book[i + 1]}\n" \
                            + "```"
                yield p.get_name(), ret_mes
        else:
            # 共有情報
            self.script_page += 1
            ret_mes = f"{self.script_page + 1}ページ目を執筆中……"
            self.script_all_set_notified = False
            self.playermaster.turn_page()
            yield None, ret_mes

            # 全員へ本文執筆の通知
            for p in self.playermaster.get_players():
                target_book_title = self.playermaster.get_target_book_title\
                                                            (p.get_name())
                target_last_script = self.playermaster.get_target_last_script\
                                                            (p.get_name())
                ret_mes = f"{ICON} 本「{target_book_title}」の{self.script_page + 1}ページ目を書き込んでください。\n" \
                        + f"{self.script_page}ページ目の内容は以下の通りでした。\n" \
                        + "```\n" \
                        + f"{target_last_script}\n" \
                        + "```"
                yield p.get_name(), ret_mes
    
    def initialize(self) -> None:
        self.members = [member for member in self.get_all_members()]
        self.playermaster = PlayerMaster()

        self.allowed_commands_per_phase = {}
        for p in PHASES.values():
            self.allowed_commands_per_phase[p] = []
            for c in ALLOWED_COMMANDS_PER_PHASE[p] + ALWAYS_ALLOWED_COMMANDS:
                self.allowed_commands_per_phase[p]\
                                .append(COMMANDS[c].get_command())

        self.function_dictionary = {
            COMMANDS["HLP"].get_command(): self.help,
            COMMANDS["SHOWPL"].get_command(): self.show_players,
            COMMANDS["JOIN"].get_command(): self.join,
            COMMANDS["LEAVE"].get_command(): self.leave,
            COMMANDS["RESETMMB"].get_command(): self.reset_players,
            COMMANDS["SETCYCLES"].get_command(): self.set_cycles,
            COMMANDS["SETCH"].get_command(): self.set_channel,
            COMMANDS["START"].get_command(): self.start_game,
            COMMANDS["QUITGM"].get_command(): self.quit_game,
            COMMANDS["SETTITLE"].get_command(): self.set_title,
            COMMANDS["STARTSCRPT"].get_command(): self.start_script,
            COMMANDS["SETSCRPT"].get_command(): self.set_script,
            COMMANDS["NEXT"].get_command(): self.next_turn,
        }

        self.phase = PHASES["S"]
        self.cycles = 1

        print("initialization ok")
    
    def load_channel(self, id: int) -> None:
        self.gamech_id = id
