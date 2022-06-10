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
        if "\n" in script:
            raise LineBreakForbiddenError()
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
