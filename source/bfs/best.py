#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import random
from typing import Dict, List, Union


DEFAULT_BEST_THEMES = os.path.join(os.path.dirname(__file__), "themes.json")

class InvalidThemesError(Exception):
    pass

class Best:
    _current_theme: str
    _th_list: List[str]
    num_theme: int

    def __init__(self, th_path: Union[str, None]) -> None:
        self.num_theme = 0
        self._current_theme = ""
        self._load_theme_list(th_path)
    
    def _load_theme_list(self, th_path: Union[str, None]) -> None:
        if th_path is None:
            th_path = DEFAULT_BEST_THEMES
        
        with open(th_path, "r") as f:
            try:
                self._th_list: List[dict] = json.loads(f.read())["theme_list"]
            except KeyError:
                raise InvalidThemesError()
        
        self.num_theme = len(self._th_list)
    
    def _set_theme(self, i: Union[int, None]) -> None:
        if i is None:
            i = random.randint(0, len(self._th_list) - 1)
        elif i >= len(self._th_list):
            raise IndexError()

        self._current_theme = self._th_list[i]
    
    def get_random_theme(self) -> str:
        self._set_theme(None)

        return self._current_theme


class BestOptions:
    _option_dict: Dict[int, Union[str, None]]
    _answerer_id: int

    def __init__(self, len: int):
        self._option_dict = {}
        for i in range(len):
            self._option_dict[i] = None
        self._answerer_id = 0
    
    def set_answerer_id(self, i: int) -> None:
        if not i in list(self._option_dict.keys()):
            raise IndexError()
        
        self._answerer_id = i

    def set_option(self, i: int, text: str) -> None:
        if not i in list(self._option_dict.keys()):
            raise IndexError()
        
        self._option_dict[i] = text
    
    def all_set(self) -> bool:
        ret = True
        for i in range(len(self._option_dict)):
            if i == self._answerer_id:
                continue
            if self._option_dict.get(i) is None:
                ret = False

        return ret

    def list_random(self) -> List[str]:
        assert self.all_set()

        tmp: List[str] = []
        for i in range(len(self._option_dict)):
            if i == self._answerer_id:
                continue
            tmp.append(self._option_dict.get(i))
        random.shuffle(tmp)
        return tmp
