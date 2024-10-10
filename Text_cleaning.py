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
    def __init__(self, line: int, column: int, word: str, type: int):
        self.line = line
        self.column = column
        self.word = word
        self.type = type

class Identify:
    @staticmethod
    def remove_space(pre_space: List[Row]) -> List[Row]:
        """Removes unnecessary spaces between numbers and symbols."""
        cleaned_rows = []

        for i in range(len(pre_space)):
            if pre_space[i].word:
                if pre_space[i].word == ".":
                    # Combine with previous and next rows if they are numbers
                    if (i > 0 and pre_space[i - 1].type in {DataType.INT32, DataType.INT64}) and \
                       (i < len(pre_space) - 1 and pre_space[i + 1].type in {DataType.INT32, DataType.INT64}):
                        pre_space[i - 1].word += pre_space[i].word + pre_space[i + 1].word
                        pre_space[i - 1].type = DataType.DOUBLE
                        pre_space[i + 1].word = ""  # Clear the next word
                        pre_space[i + 1].type = DataType.STRING  # Reset type
                else:
                    cleaned_rows.append(pre_space[i])  # Keep the current row if not processed

        return cleaned_rows

    @staticmethod
    def string_type(word: str) -> int:
        """Identifies the data type of a given word."""
        if word is None or word.strip() == "":
            return DataType.STRING
        
        # Remove currency symbol
        word = re.sub(r"\$", "", word)

        # Check for integer
        if word.isdigit():
            return DataType.INT32
        
        # Check for float
        try:
            float(word)
            return DataType.DOUBLE
        except ValueError:
            pass

        # Check for date in MM/DD/YYYY format
        try:
            datetime.strptime(word, "%m/%d/%Y")
            return DataType.DATETIME
        except ValueError:
            pass

        return DataType.STRING