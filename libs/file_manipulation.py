import json
import os
import zipfile

def export_json_to_file(data, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)

def import_json_from_file(file_path):
    with open(file_path, 'r') as infile:
        data = json.load(infile)
    return data 

def export_string_to_file(text, file_path):
    with open(file_path, 'w') as outfile:
        outfile.write(text)

def import_string_from_file(file_path):
    with open(file_path, 'r') as infile:
        text = infile.read()
    return text

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def zip_and_delete_files(folder_path, zip_name):
    # Create a new Zip file
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Iterate through files in the folder
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Add the file to the Zip archive
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
                # Delete the original file
                os.remove(file_path)


