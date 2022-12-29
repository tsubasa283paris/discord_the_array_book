#!/usr/bin/env python
# -*- coding: utf-8 -*-

class InvalidPageError(Exception):
    pass

class LineBreakForbiddenError(Exception):
    pass

class Poetry:
    _letters: list # of string or None
    _pattern: list # of int
    _max_letters_per_column: int

    def __init__(self, pattern: list, max_letters_per_column: int) -> None:
        self._letters = []
        self._pattern = pattern
        self._max_letters_per_column = max_letters_per_column
    
    def add_letter(self) -> None:
        self._letters.append(None)
    
    def set_letter(self, letter: str, index: int) -> None:
        if index > len(self._letters):
            raise InvalidPageError()
        elif index == len(self._letters):
            self._letters.append(letter)
        else:
            self._letters[index] = letter
    
    def get_letters(self) -> list:
        return self._letters
    
    def generate_vertical(self) -> str:
        """
        縦書き表記の文字列を返す。
        """
        columns = [[]]
            
        c = 0
        j = 0
        c_j = 0
        for i in range(len(self._letters)):
            columns[c].append(self._letters[i])
            j += 1
            c_j += 1
            if j >= self._pattern[c]:
                columns.append([])
                c += 1
                j = 0
                c_j = 0
            elif c_j >= self._max_letters_per_column:
                columns.append([])
                c += 1
                c_j = 0
        
        ret_str = ""
        for i in range(max(len(column) for column in columns)):
            row = []
            for j in reversed(range(len(columns))):
                if len(columns[j]) <= i:
                    row.append("　")
                else:
                    if columns[j][i] is None:
                        row.append("○")
                    else:
                        row.append(columns[j][i])
            ret_str += " ".join(row) + "\n"

        return ret_str.rstrip("\n")