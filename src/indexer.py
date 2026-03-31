import re


def tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    return words
