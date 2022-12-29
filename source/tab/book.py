#!/usr/bin/env python
# -*- coding: utf-8 -*-

class InvalidPageError(Exception):
    pass

class LineBreakForbiddenError(Exception):
    pass

class Book:
    _title: str or None
    _scripts: list # of string or None

    def __init__(self) -> None:
        self._title = None
        self._scripts = []
    
    def set_title(self, title: str) -> None:
        if "\n" in title:
            raise LineBreakForbiddenError()
        self._title = title
    
    def add_page(self) -> None:
        self._scripts.append(None)
    
    def set_script(self, script: str, page: int) -> None:
        if page > len(self._scripts):
            raise InvalidPageError()
        elif page == len(self._scripts):
            self._scripts.append(script)
        else:
            self._scripts[page] = script
    
    def get_title(self) -> str:
        return self._title
    
    def get_scripts(self) -> list:
        return self._scripts
    
    def generate_markdown(self, pln_list: list) -> str:
        """
        pln_list: プレイヤー名のリスト。記述順に入っている（先頭がオーナー）
        """
        ret_str = ""
        ret_str += f"# 「{self._title}」\n"
        ret_str += f"作：{pln_list[0]}\n\n"

        for i in range(len(self._scripts)):
            ret_str += f"## {i + 1} ({pln_list[i % len(pln_list)]})\n\n"
            lines = self._scripts[i].splitlines()
            for j in range(len(lines)):
                if len(lines[j]) == 0:
                    ret_str += "\n"
                else:
                    ret_str += lines[j] + "  \n"
            ret_str += "\n"

        return ret_str