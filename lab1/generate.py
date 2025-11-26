import random
import string
import calendar
from datetime import date

START_YEAR = 1
END_YEAR = 2077

def generate_random_date():
    year = random.randint(START_YEAR, END_YEAR)
    month = random.randint(1, 12)

    if month == 2:
        if calendar.isleap(year):
            day = random.randint(1, 29)
        else:
            day = random.randint(1, 28)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30) 
    else:
        day = random.randint(1, 31)

    return date(year, month, day)

def generate_data(file, file_size_mb, max_string_len):
    print(f"GENERATING FRESH DATA [Size: {file_size_mb} MB, Max string length: {max_string_len}]")

    with open(file, "w") as f:
        size = 0
        lines = 0
        target = file_size_mb * 1024 * 1024

        while size < target:
            rand_num = str(random.randint(0, 99999))
            rand_string = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1, max_string_len)))
            rand_date = generate_random_date()

            line = f"{rand_num} - {rand_string} - {rand_date.strftime('%d.%m.%Y')}\n"

            f.write(line)
            size += len(line)
            lines += 1

    print(f"FILE DATA GENERATED SUCCESSFULLY [{lines} lines]")
