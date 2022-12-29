#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from source.aap.poetry import Poetry

class UnknownPlayerError(Exception):
    pass

class Player:
    _name: str
    _poetry: Poetry
    
    def __init__(self, name: str, pattern: list, max_letters_per_column: int) -> None:
        self._name = name
        self._poetry = Poetry(pattern, max_letters_per_column)
    
    def get_name(self) -> str:
        return self._name
    
    def reset_poetry(self, pattern: list, max_letters_per_column: int) -> None:
        self._poetry = Poetry(pattern, max_letters_per_column)
    
    def add_poetry_letter(self) -> None:
        self._poetry.add_letter()
    
    def set_poetry_letter(self, letter: str, index: int) -> None:
        self._poetry.set_letter(letter, index)

    def latest_letter_is_set(self) -> bool:
        return self._poetry.get_letters()[-1] is not None
    
    def get_poetry(self) -> Poetry:
        return self._poetry

    def get_displayable_poetry(self) -> str:
        return self._poetry.generate_vertical()

class PlayerMaster:
    _players: list # of Player
    _rand_indexes: list # of int
    _name_index_map: dict # of str: int
    _pattern: list # of int
    _max_letters_per_column: int

    def __init__(self, pattern: list, max_letters_per_column: int):
        self._players = []
        self._rand_indexes = []
        self._name_index_map = {}
        self._pattern = pattern
        self._max_letters_per_column = max_letters_per_column
    
    def set_pattern(self, pattern: list):
        self._pattern = pattern
        for player in self._players:
            player.reset_poetry(self._pattern, self._max_letters_per_column)
    
    def set_max_letters_per_column(self, max_letters_per_column: int):
        self._max_letters_per_column = max_letters_per_column
        for player in self._players:
            player.reset_poetry(self._pattern, self._max_letters_per_column)

    def add_player(self, player_name: str) -> bool:
        ok = True
        for player in self._players:
            if player.get_name() == player_name:
                ok = False
        if ok:
            self._players.append(Player(player_name, self._pattern, self._max_letters_per_column))
        return ok
    
    def remove_player(self, player_name: str) -> bool:
        found = False
        for i, player in enumerate(self._players):
            if player.get_name() == player_name:
                self._players.pop(i)
                found = True
        return found
    
    def remove_all(self) -> None:
        self._players = []
    
    def display_players(self) -> str:
        ret_str = "\n".join([
            f"{i + 1:3d}: {self._players[i].get_name()}"
            for i in range(len(self._players))
        ])
        return ret_str

    def get_players(self) -> list:
        return self._players

    def len_players(self) -> int:
        return len(self._players)

    def setup(self) -> None:
        self._rand_indexes = list(range(len(self._players)))
        random.shuffle(self._rand_indexes)
        for i in range(len(self._players)):
            self._players[i].reset_poetry(self._pattern, self._max_letters_per_column)
            p_name = self._players[i].get_name()
            self._name_index_map[p_name] = i
            self._players[i].add_poetry_letter()
    
    def get_target_poetry(self, player_name: str) -> str:
        target_poetry_index = self._name_index_map.get(player_name)
        if target_poetry_index is None:
            raise UnknownPlayerError()
        return self._players[target_poetry_index].get_displayable_poetry()
    
    def set_poetry_letter(self, player_name: str, letter: str, index: int) \
                                                                -> bool:
        target_poetry_index = self._name_index_map.get(player_name)
        if target_poetry_index is None:
            raise UnknownPlayerError()
        self._players[target_poetry_index].set_poetry_letter(letter, index)
        return self.latest_letters_are_set()
    
    def next_letter(self) -> None:
        for i in range(len(self._players)):
            p_name = self._players[i].get_name()
            next_i = find_next(self._rand_indexes,
                                self._name_index_map[p_name])
            self._name_index_map[p_name] = self._rand_indexes[next_i]
            self._players[i].add_poetry_letter()

    def latest_letters_are_set(self) -> bool:
        return all(p.latest_letter_is_set() for p in self._players)

def find_next(l: list, v: any) -> int:
    key_i = -1
    for i in range(len(l)):
        if l[i] == v:
            key_i = i
            break
    if key_i < 0:
        raise ValueError()
    return (key_i + 1) % len(l)

def cycle_until(l: list, v: any) -> list:
    key_i = -1
    for i in range(len(l)):
        if l[i] == v:
            key_i = i
            break
    if key_i < 0:
        raise ValueError()
    return l[key_i:] + l[:key_i]
