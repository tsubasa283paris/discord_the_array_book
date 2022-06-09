#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from source.book import Book

class UnknownPlayerError(Exception):
    pass

class Player:
    _name: str
    _book: Book
    
    def __init__(self, name: str) -> None:
        self._name = name
        self._book = Book()
    
    def get_name(self) -> str:
        return self._name
    
    def reset_book(self) -> None:
        self._book = Book()

    def get_book_title(self) -> str:
        return self._book.get_title()

    def set_book_title(self, title: str) -> None:
        self._book.set_title(title)
    
    def add_book_page(self) -> None:
        self._book.add_page()
    
    def get_book_scripts(self) -> list:
        return self._book.get_scripts()
    
    def set_book_script(self, script: str, page: int) -> None:
        self._book.set_script(script, page)
    
    def title_is_set(self) -> bool:
        return self._book.get_title() is not None

    def latest_script_is_set(self) -> bool:
        return self._book.get_scripts()[-1] is not None


class PlayerMaster:
    _players: list # of Player
    _rand_indexes: list # of int
    _name_index_map: dict # of str: int

    def __init__(self):
        self._players = []
        self._rand_indexes = []

    def add_player(self, player_name: str) -> bool:
        ok = True
        for player in self._players:
            if player.get_name() == player_name:
                ok = False
        if ok:
            self._players.append(Player(player_name))
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
            p_name = self._players[i].get_name()
            self._name_index_map[p_name] = self._rand_indexes[i]
            self._players[i].add_book_page()
    
    def get_target_book_title(self, player_name: str) -> str:
        target_book_index = self._name_index_map.get(player_name)
        if target_book_index is None:
            raise UnknownPlayerError()
        return self._players[target_book_index].get_book_title()
    
    def set_book_title(self, player_name: str, title: str) -> bool:
        found = False
        for p in self._players:
            if p.get_name() == player_name:
                found = True
                p.set_book_title(title)
        if not found:
            raise UnknownPlayerError()
        return self.titles_are_set()
    
    def get_target_last_script(self, player_name: str) -> str:
        target_book_index = self._name_index_map.get(player_name)
        if target_book_index is None:
            raise UnknownPlayerError()
        return self._players[target_book_index].get_book_scripts()[-2]
    
    def set_book_script(self, player_name: str, script: str, page: int) \
                                                                -> bool:
        target_book_index = self._name_index_map.get(player_name)
        if target_book_index is None:
            raise UnknownPlayerError()
        self._players[target_book_index].set_book_script(script, page)
    
    def turn_page(self) -> None:
        for p in self._players:
            p.add_book_page()
    
    def titles_are_set(self) -> bool:
        return all(p.title_is_set() for p in self._players)

    def latest_scripts_are_set(self) -> bool:
        return all(p.latest_script_is_set() for p in self._players)