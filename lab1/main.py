from generate import generate_data
import time
import math
import os

FILES_BASE_PATH = "./files"

def extract_key_from_line(line):
    return int(line.partition(' ')[0])

def format_time(seconds):
    time_output = ""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds_left = seconds % 60

    if hours >= 1:
        time_output += f"{hours} hours, "

    if minutes >= 1:
        time_output += f"{minutes} minutes, "

    time_output += f"{round(seconds_left, 2)} seconds"
    
    return time_output

def check_sorted(main_file):
    prev = -1

    with open(f"{FILES_BASE_PATH}/{main_file}", "r") as file:
        for line in file:
            cur = extract_key_from_line(line)

            if prev > cur:
                return False
            
            prev = cur

        return True

def merge_files(main_file, file0="0.txt", file1="1.txt"):
    with open(f"{FILES_BASE_PATH}/{file0}", 'r') as f0, \
         open(f"{FILES_BASE_PATH}/{file1}", 'r') as f1, \
         open(f"{FILES_BASE_PATH}/{main_file}", 'w') as main_f:
        
        line0 = f0.readline()
        line1 = f1.readline()

        while line0 and line1:
            key0 = extract_key_from_line(line0)
            key1 = extract_key_from_line(line1)

            if key0 <= key1:
                main_f.write(line0)
                line0 = f0.readline()
            else:
                main_f.write(line1)
                line1 = f1.readline()

        if line0:
            main_f.write(line0)
            for rest in f0:
                main_f.write(rest)
        
        if line1:
            main_f.write(line1)
            for rest in f1:
                main_f.write(rest)

def distribute_data(filename, file0="0.txt", file1="1.txt"):
    prev = - (math.inf)
    file_flag = 0

    with open(f"{FILES_BASE_PATH}/{filename}", "r") as main_f, \
            open(f"{FILES_BASE_PATH}/{file0}", "w") as f0, \
            open(f"{FILES_BASE_PATH}/{file1}", "w") as f1:

            temp_files = [f0, f1]
            
            for line in main_f:
                cur = extract_key_from_line(line)

                if prev > cur:
                    file_flag += 1
                
                temp_files[file_flag % 2].write(line)

                prev = cur

def sort_adaprive_asc(filename, file0="0.txt", file1="1.txt", file_size_mb=10, max_string_len=20):
    generate_data(f"{FILES_BASE_PATH}/{filename}", file_size_mb, max_string_len)

    start_time = time.time()
    print(f"STARTING SORTING PROCESS... [{start_time}]")

    while not check_sorted(filename):
        distribute_data(filename)
        merge_files(filename)

    os.remove(f"{FILES_BASE_PATH}/{file0}")
    os.remove(f"{FILES_BASE_PATH}/{file1}")

    end_time = time.time()

    print(f"SORTING EXECUTED SUCCESSFULLY [{end_time}]")
    print("PROCESSING TIME:", format_time(end_time - start_time), f"[{end_time - start_time} seconds]")

sort_adaprive_asc("data.txt", file_size_mb=0.05)