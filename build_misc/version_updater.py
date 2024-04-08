import os
import datetime


LAST_VERSION_FILENAME = "last_version.txt"

dt_now = datetime.datetime.now()

if not os.path.exists(LAST_VERSION_FILENAME):
    with open(LAST_VERSION_FILENAME, "w", encoding="utf-8") as f:
        f.write("0.0.0.0")


with open(LAST_VERSION_FILENAME, "r", encoding="utf-8") as f:
    string = f.read()

year, month, day, number = [int(el) for el in string.split(".")]

if dt_now.date() == datetime.date(year, month, day):
    number += 1
else:
    year = dt_now.year
    month = dt_now.month
    day = dt_now.day
    number = 0

version = f"{year}.{month}.{day}.{number}"

with open(LAST_VERSION_FILENAME, "w", encoding="utf-8") as f:
    f.write(version)

print(f"New version is {version}")
