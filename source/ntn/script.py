#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import random
from typing import Dict, List, Union


DEFAULT_SCRIPT_LAYOUT = os.path.join(os.path.dirname(__file__), "layout.json")

class InvalidLayoutError(Exception):
    pass

class Script:
    num_blank: Union[int, None]
    num_layout: int
    _blank_pattern: Union[str, None]
    _lo_list: List[dict]
    _layout: Union[str, None]
    _id_word_map: Union[Dict[int, Union[str, None]], None]

    def __init__(self, lo_path: Union[str, None]) -> None:
        self._load_layout_dict(lo_path)
        self.num_blank = None
        self._blank_pattern = None
        self._layout = None
        self._id_word_map = None
    
    def _load_layout_dict(self, lo_path: Union[str, None]) -> None:
        if lo_path is None:
            lo_path = DEFAULT_SCRIPT_LAYOUT
        
        self._lo_list: List[dict] = json.loads(lo_path)["layout_list"]
        self.num_layout = len(self._lo_list)
    
    def set_layout(self, i: Union[int, None]) -> None:
        if i is None:
            i = random.randint(0, len(self._lo_list) - 1)
        lo = self._lo_list[i]

        self.num_blank = lo["num_blank"]
        self._blank_pattern = lo["blank_pattern"]
        self._layout = lo["layout"]

        for i in range(self.num_blank):
            self._id_word_map[i] = None
    
    def show_script(self) -> str:
        disp_script: str = self._layout
        for i in range(self.num_blank):
            if self._id_word_map[i] is not None:
                disp_script = disp_script.replace(
                    self._blank_pattern.replace("N", str(i + 1)),
                    f"[ {self._id_word_map[i]} ]",
                )
        return disp_script
    
    def show_script_blank(self) -> str:
        disp_script: str = self._layout
        for i in range(self.num_blank):
            disp_script = disp_script.replace(
                self._blank_pattern.replace("N", str(i)),
                f"[ {i + 1} ]",
            )
        return disp_script
    
    def show_script_limit_open(self, open_ids: List[int]) -> str:
        disp_script: str = self._layout
        for i in open_ids:
            if self._id_word_map[i] is not None:
                disp_script = disp_script.replace(
                    self._blank_pattern.replace("N", str(i)),
                    f"[ {i + 1} ]",
                )
        return disp_script
    
    def fill_blank(self, i: int, word: str) -> None:
        if i >= self.num_blank:
            raise ValueError()

        self._id_word_map[i] = word
    
    def is_filled(self, i: int) -> bool:
        return self._id_word_map[i] is not None
    
    def all_filled(self) -> bool:
        return all(self._id_word_map[i] is not None for i in range(len(self.num_blank)))
