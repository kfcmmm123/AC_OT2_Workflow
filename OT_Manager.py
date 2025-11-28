import re

def verifyAddress(s, numCols: int, numRows: int):
    return bool(re.match(r"^[A-Z]\d+$", s)) and int(s[1:]) <= numCols and (ord(s[0]) - 64) <= numRows