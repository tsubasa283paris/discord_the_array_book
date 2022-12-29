#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord
import mojimoji

from source.command import Command
from source.game_controller import GameController, COMMANDS_B, ALWAYS_ALLOWED_COMMANDS_B
from source.aap.player import PlayerMaster, UnknownPlayerError

DEFAULT_PATTERN = [5, 7, 5]
MAX_LET_PER_COL = 10
ALLOWED_LETTERS = "0123456789" \
                + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" \
                + "０１２３４５６７８９" \
                + "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ" \
                + "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ" \
                + "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほ" \
                + "まみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでど" \
                + "ばびぶべぼぱぴぷぺぽぁぃぅぇぉゃゅょゎ" \
                + "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホ" \
                + "マミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデド" \
                + "バビブベボパピプペポァィゥェォヵャュョヮー"
ICONS_A = {
    "MAIN": ":book:",
    "CAUT": ":exclamation:",
}
COMMANDS_A = {
    "SHOWPL": Command("!show_players", "ゲーム参加メンバーリストを表示します。"),
    "JOIN": Command("!join", "ゲーム参加メンバーリストに追加されます。"),
    "LEAVE": Command("!leave", "ゲーム参加メンバーリストから除外されます。"),
    "RESETMMB": Command("!reset_players", "ゲーム参加メンバーリストを全消去します。"),
    "SETPAT": Command("!set_pattern", "文字数の型を設定します。"),
    "START": Command("!start_game", "ゲームを開始します。"),
    "QUITGM": Command("!quit_game", "ゲームを強制終了します。"),
    "SETLET": Command("!set_letter", "文字を入力します。"),
}
PHASES = {
    "S": "standby",
    "G": "game",
}
ALLOWED_COMMANDS_PER_PHASE_A = {
    PHASES["S"]: [
        "JOIN",
        "LEAVE",
        "RESETMMB",
        "SETPAT",
        "LNCG",
        "SETCH",
        "RELOADMMB",
        "START",
    ],
    PHASES["G"]: [
        "QUITGM",
        "SETLET",
    ],
}
ALWAYS_ALLOWED_COMMANDS_A = [
    "SHOWPL",
]
ALWAYS_ALLOWED_COMMANDS_A += ALWAYS_ALLOWED_COMMANDS_B

class AAPController(GameController):
    allowed_commands_per_phase: dict # of str: str
    commands_dictionary: dict # of str: Command
    function_dictionary: dict # of str: function
    gamech_id: int
    phase: str
    pattern: list # of int
    members: list # of discord.Member
    playermaster: PlayerMaster
    poetry_index: int

    def initialize(self, get_all_members, gamech_id: int):
        self.get_all_members = get_all_members
        self.gamech_id = gamech_id
        self.pattern = DEFAULT_PATTERN
        self.members = [member for member in self.get_all_members()]
        self.playermaster = PlayerMaster(self.pattern, MAX_LET_PER_COL)
        self.poetry_index = 0

        self.commands_dictionary = COMMANDS_A
        self.commands_dictionary.update(COMMANDS_B)

        self.allowed_commands_per_phase = {}
        for p in PHASES.values():
            self.allowed_commands_per_phase[p] = []
            for c in ALLOWED_COMMANDS_PER_PHASE_A[p] + ALWAYS_ALLOWED_COMMANDS_A:
                self.allowed_commands_per_phase[p]\
                                .append(self.commands_dictionary[c].get_command())

        self.function_dictionary = {
            self.commands_dictionary["HLP"].get_command(): self.help,
            self.commands_dictionary["SHOWPL"].get_command(): self.show_players,
            self.commands_dictionary["JOIN"].get_command(): self.join,
            self.commands_dictionary["LEAVE"].get_command(): self.leave,
            self.commands_dictionary["RESETMMB"].get_command(): self.reset_players,
            self.commands_dictionary["SETPAT"].get_command(): self.set_pattern,
            self.commands_dictionary["SETCH"].get_command(): self.set_channel,
            self.commands_dictionary["RELOADMMB"].get_command(): self.reload_member,
            self.commands_dictionary["START"].get_command(): self.start_game,
            self.commands_dictionary["QUITGM"].get_command(): self.quit_game,
            self.commands_dictionary["SETLET"].get_command(): self.set_letter,
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
            ret_mes = f"{ICONS_A['MAIN']} {author.name}の参加を承りました。"
            return ((None, ret_mes),)
    
    def leave(self, _, author: discord.Member) -> tuple:
        if self.playermaster.remove_player(author.name):
            ret_mes = f"{ICONS_A['MAIN']} {author.name}の参加を取り消しました。"
            return ((None, ret_mes),)
    
    def reset_players(self, *_) -> tuple:
        ret_mes = f"{ICONS_A['MAIN']} 参加メンバーをリセットしました。"
        self.playermaster.remove_all()
        return ((None, ret_mes),)
    
    def set_pattern(self, content: str, author: discord.Member) -> tuple:
        ok = True
        pattern_items = content.split(",")
        pattern = []
        try:
            for pattern_item in pattern_items:
                pattern.append(int(pattern_item))
        except ValueError:
            ok = False
        if ok:
            self.pattern = pattern
            self.playermaster.set_pattern(self.pattern)
            ret_mes = f"{ICONS_A['MAIN']} 詩の型が{pattern}に設定されました。"
            ret_mem = None
        else:
            ret_mes = f"{ICONS_A['CAUT']} 与えられた文字が数字として解釈できません。"
            ret_mem = author.name
        return ((ret_mem, ret_mes),)

    def start_game(self, *_) -> tuple:
        ret = []
        # 共有情報
        ret_mes = f"{ICONS_A['MAIN']} **ゲームを開始します！**\n" \
                + "ここからは参加者全員の個人チャットにて案内をいたします。\n\n" \
                + "参加者一覧：\n"
        for p in self.playermaster.get_players():
            ret_mes += f"- {p.get_name()}\n"
        self.playermaster.setup()
        self.phase = PHASES["G"]
        self.poetry_index = 0
        ret.append((None, ret_mes))

        # 全員へ操作方法の通知
        cmd = self.commands_dictionary["SETLET"].get_command()
        ret_mes = f"{ICONS_A['MAIN']} `{cmd}` のあとに一文字打ち込み、表示される◯の位置の文字を設定してください。\n" \
                + "ゲームマスターが次のターンに移行するまでは何度でも上書きできます。"
        for p in self.playermaster.get_players():
            ret.append((p.get_name(), ret_mes))
        
        return ret
    
    def quit_game(self, *_) -> tuple:
        ret_mes = f"{ICONS_A['MAIN']} ゲームが強制終了されました。\n" \
                + "（参加メンバーは保存されています。）"
        self.phase = PHASES["S"]
        return ((None, ret_mes),)
    
    def set_letter(self, content: str, author: discord.Member) -> tuple:
        ret = []
        if len(content) > 1:
            ret_mes = f"{ICONS_A['CAUT']} 送信できるのは1文字までです！"
            return ((author.name, ret_mes),)
        elif not content in ALLOWED_LETTERS:
            ret_mes = f"{ICONS_A['CAUT']} 無効な文字です！"
            return ((author.name, ret_mes),)
        letter = mojimoji.han_to_zen(content)
        if letter == "ー":
            letter = "｜"
        ret_mes = f"{ICONS_A['MAIN']} {self.poetry_index + 1}文字目の変更を受け付けました！"
        all_set = False
        try:
            all_set = self.playermaster.set_poetry_letter\
                                    (author.name, letter, self.poetry_index)
        except UnknownPlayerError:
            ret_mes = f"{ICONS_A['CAUT']} ゲームに参加していません！"
        ret.append((author.name, ret_mes))

        if all_set:
            # 全員がi文字目を設定した段階で次のターンに移る
            if self.poetry_index == sum(self.pattern) - 1:
                # 最終文字が終了した場合

                # 全員へ完成した本文を送付する
                players = self.playermaster.get_players()
                for p in players:
                    ret_mes = f"{ICONS_A['MAIN']} あなたの送り出した詩が完成しました！\n" \
                            + "```\n" \
                            + f"{p.get_displayable_poetry()}\n" \
                            + "```"
                    ret.append((p.get_name(), ret_mes))

                # 共有情報
                ret_mes = f"{ICONS_A['MAIN']} 全員の詩が完成しました！参加者全員の個人チャットに完成した詩を送付しました。"
                self.phase = PHASES["S"]
                ret.append((None, ret_mes))
            else:
                # 共有情報
                self.poetry_index += 1
                ret_mes = f"{self.poetry_index + 1}文字目を執筆中……"
                self.playermaster.next_letter()
                ret.append((None, ret_mes))

                # 全員へ本文執筆の通知
                for p in self.playermaster.get_players():
                    ret_mes = f"{ICONS_A['MAIN']} あなたの前のターンの詩の内容は以下の通りでした。\n" \
                            + "```\n" \
                            + f"{self.playermaster.get_target_poetry(p.get_name())}\n" \
                            + "```"
                    ret.append((p.get_name(), ret_mes))
        
        return ret
