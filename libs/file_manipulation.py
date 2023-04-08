import json

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