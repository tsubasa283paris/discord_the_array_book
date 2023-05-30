#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Union


class UnknownPlayerError(Exception):
    pass

class Player:
    _name: str
    
    def __init__(self, name: str) -> None:
        self._name = name
    
    def get_name(self) -> str:
        return self._name

class PlayerMaster:
    _player_list: List[Player]

    def __init__(self):
        self._player_list = []
    
    def add_player(self, player_name: str) -> bool:
        ok = True
        for player in self._player_list:
            if player.get_name() == player_name:
                ok = False
        if ok:
            self._player_list.append(Player(player_name))
        return ok
    
    def remove_player(self, player_name: str) -> bool:
        found = False
        for i, player in enumerate(self._player_list):
            if player.get_name() == player_name:
                self._player_list.pop(i)
                found = True
        return found
    
    def remove_all(self) -> None:
        self._player_list = []
    
    def display_players(self) -> str:
        ret_str = "\n".join([
            f"{i + 1:3d}: {self._player_list[i].get_name()}"
            for i in range(len(self._player_list))
        ])
        return ret_str
    
    def get_player(self, player_name: str) -> Union[Player, None]:
        for player in self._player_list:
            if player.get_name() == player_name:
                return player
        return None

    def get_players(self) -> List[Player]:
        return self._player_list

    def len_players(self) -> int:
        return len(self._player_list)

