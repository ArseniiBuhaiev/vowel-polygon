from random import choice

with open("names.txt", "r", encoding="utf-8") as f:
    names = [name for name in f]

print(choice(names).strip())