#!/usr/bin/env python3

import json
import os
import csv
import pandas as pd

leeway_time = 2 # 2 seconds before the start time, 2 seconds after the end time

output_folder = "output"

# Function to load JSON data
def load_json(file_path):
    print("Loading " + file_path)
    with open(file_path, 'r') as file:
        # Get first line
        data = json.load(file)
    return data

# Function to load CSV data
def load_csv(file_path):
    return pd.read_csv(file_path)

# Function to write CSV data
def write_csv(data, file_path):
    data.to_csv(file_path, index=False)

# Function to process the data and generate new CSVs
def process_data(power_data, exp_file_path, exp_file_info):
    # Implement processing logic based on specific requirements.
    # For example, slicing power_data based on relevant time frame.
    # ...
    start_time, end_time = get_start_end_time(exp_file_path)
    power_data['Hour:Minute:Second'] = pd.to_datetime(power_data['Hour:Minute:Second'], format='%H:%M:%S')
    power_data = power_data.set_index('Hour:Minute:Second')
    start_time = pd.to_datetime(start_time, format='%H:%M:%S') - pd.Timedelta(seconds=leeway_time)
    end_time = pd.to_datetime(end_time, format='%H:%M:%S') + pd.Timedelta(seconds=leeway_time)
    # Get rid of the date
    start_time = start_time.time()
    end_time = end_time.time()
    power_data = power_data.between_time(start_time, end_time)
    power_data = power_data.reset_index()
    power_data['Hour:Minute:Second'] = power_data['Hour:Minute:Second'].dt.time

    # Print warning if the power data is much smaller than the experiment data
    if power_data.empty:
        print("Warning: Power data is empty.")
        return

    # print("Power Data for " + exp_file_info['name'] + ":")
    # print(power_data)
    # print(power_data.keys())

    power_data_time = pd.to_datetime(power_data['Hour:Minute:Second'].iloc[-1], format='%H:%M:%S') -\
        pd.to_datetime(power_data['Hour:Minute:Second'].iloc[0], format='%H:%M:%S')
    exp_data_time = pd.to_datetime(end_time, format='%H:%M:%S') -\
        pd.to_datetime(start_time, format='%H:%M:%S')
    # print("Power data time: " + str(power_data_time))
    # print("Experiment data time: " + str(exp_data_time))
    power_data_time = power_data_time.total_seconds()
    exp_data_time = exp_data_time.total_seconds()
    if power_data_time / exp_data_time < 0.8:
        print("(" + exp_file_info['name'] + ") Warning: Power data is much smaller than experiment data.")
        print("Power data time: " + str(power_data_time))
        print("Experiment data time: " + str(exp_data_time))

    parent_folder = os.path.split(os.path.dirname(exp_file_path))[-1]
    folder = os.path.join(output_folder, parent_folder)

    if not os.path.isdir(folder):
        os.mkdir(folder)

    write_csv(power_data, os.path.join(folder, exp_file_info['name']))

def get_start_end_time(exp_file_path):
    # Look for the first row
    df = pd.read_csv(exp_file_path)
    return df['time'].iloc[0], df['time'].iloc[-1]

# Main Function
def main():
    input_folder = 'input'

    # Iterating through all the folders inside 'input'
    for folder in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder)

        # Check if it is a folder
        if os.path.isdir(folder_path):
            names_file_path = os.path.join(folder_path, 'names.json')

            # Check if names.json exists in the folder
            if os.path.exists(names_file_path):
                names_data = load_json(names_file_path)

                # Extract and load power data
                power_file_path = os.path.join(folder_path, names_data['power'])
                power_data = load_csv(power_file_path)

                # Iterate through experiments and process data
                for exp_file_name, exp_file_info in names_data['experiments'].items():
                    exp_file_path = os.path.join(folder_path, exp_file_name)

                    # Check if the result file exists
                    if os.path.exists(exp_file_path):
                        # exp_data = load_csv(exp_file_path)

                        # Process data and create new CSVs as per the requirements
                        process_data(power_data, exp_file_path, exp_file_info)
                    else:
                        print(f"Experiment file {result_file_path} not found.")
            else:
                print(f"names.json not found in {folder_path}.")
        else:
            print(f"{folder_path} is not a directory.")

# Running the main function
if __name__ == "__main__":
    main()
