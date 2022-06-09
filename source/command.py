#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Command:
    _command: str
    _help: str

    def __init__(self, command: str, help: str) -> None:
        self._command = command
        self._help = help
    
    def get_command(self) -> str:
        return self.command
    
    def get_help(self) -> str:
        return self.help
