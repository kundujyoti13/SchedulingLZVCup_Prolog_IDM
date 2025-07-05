import os
import re

def read_data(input_file):
    arr = []
    with open(input_file, 'r') as file:
        for x, line in enumerate(file):
            if x == 0:
                slotSize = int(line)
            elif x == 1:
                teams = int(line)
            else:
                field_line = line.strip().split("\t")
                arr.append(field_line)
    
    transposed_matrix = []
    for i in range(teams):  # Iterate over the columns of the original matrix
        new_row = []
        for j in range(slotSize):
            try:
                new_row.append(arr[j][i])
            except:
                print(arr[j])
        transposed_matrix.append(new_row)
    
    return slotSize, teams, transposed_matrix


def create_availability(slotSize, teams, transposed_matrix):
    available = []
    for i in range(1, teams + 1):
        for j in range(0, slotSize):
            value = transposed_matrix[i - 1][j]
            available.append([i, j, value])
    
    return available


def write_database(data, instance_file):
    with open(instance_file, 'w') as file:
        for each in data:
            team, slot, value = each
            file.write(f"availability({team}, {slot}, {value}).")


def process_input_files(input_folder, output_folder):
    input_files = os.listdir(input_folder)
    for input_file in input_files:
        input_file_path = os.path.join(input_folder, input_file)
        
        if not input_file.endswith(".txt"):
            continue
        
        input_file_number = re.findall(r'\d+', input_file)[0]
        instance_file_name = "instance" + input_file_number + ".lp"
        instance_file = os.path.join(output_folder, instance_file_name)
        
        slotSize, teams, transposed_matrix = read_data(input_file_path)
        availability_data = create_availability(slotSize, teams, transposed_matrix)
        write_database(availability_data, instance_file)


input_folder = "./input"
output_folder = "./instances_asp"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


process_input_files(input_folder, output_folder)
