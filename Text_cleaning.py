import re
from typing import List
from datetime import datetime

class DataType:
    INT32 = 1
    INT64 = 2
    DOUBLE = 3
    DATETIME = 4
    STRING = 5

class Row:
    def __init__(self, line, column, word, type):
        self.line = line
        self.column = column
        self.word = word
        self.type = type

class Identify:
    @staticmethod
    def remove_space(pre_space: List[Row]) -> List[Row]:
        """Removes unnecessary spaces between numbers and symbols."""
        for i in range(len(pre_space)):
            if pre_space[i].word:
                if re.search(r'\d\.$', pre_space[i].word):
                    find_pre_space = pre_space[i].word

                if pre_space[i].word == ".":
                    if pre_space[i - 1].type in {DataType.INT32, DataType.INT64}:
                        if pre_space[i + 1].type in {DataType.INT32, DataType.INT64}:
                            pre_space[i - 1].word += pre_space[i].word + pre_space[i + 1].word
                            pre_space[i - 1].type = DataType.DOUBLE
                            pre_space[i].word = ""
                            pre_space[i].type = DataType.STRING
                            pre_space[i + 1].word = ""
                            pre_space[i + 1].type = DataType.STRING
        return pre_space

    @staticmethod
    def string_type(word: str):
        """Identifies the data type of a given word."""
        if word is None:
            return DataType.STRING
        
        word = re.sub(r"\$", "", word)
        if word == "":
            return DataType.STRING

        try:
            int(word)
            return DataType.INT32
        except ValueError:
            try:
                float(word)
                return DataType.DOUBLE
            except ValueError:
                try:
                    datetime.strptime(word, "%m/%d/%Y")
                    return DataType.DATETIME
                except ValueError:
                    return DataType.STRING
