import json
import os
import zipfile
from io import BytesIO
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from pydub import AudioSegment


def get_blob_client(container_name, blob_name):
    connection_string = os.environ["AZURE_CONNECTION_STRING"]
    blob_client = BlobClient.from_connection_string(connection_string, container_name, blob_name)
    return blob_client

# TODO: fix/setup authentication
def get_blob_service_client():
    account_name = "<your_storage_account_name>"
    account_url = f"https://{account_name}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    return blob_service_client

# file environment specifies if azure context or local context
# example usages:
# # Save JSON data to a local file
#export_json_to_file(data, "local_file.json")
# Save JSON data to Azure Storage
#export_json_to_file(data, "container_name/blob_name.json", file_environment='AZURE')
def export_json_to_file(data, file_path, file_env='OS'):
    if file_env == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        
        json_data = json.dumps(data)
        blob_client.upload_blob(json_data, overwrite=True)
    elif file_env == 'OS':
        # create directory if it doesn't exist
        directory_path = os.path.dirname(file_path)
        create_directory_if_not_exists(directory_path)
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile)
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")

def import_json_from_file(file_path, file_env='OS'):
    if file_env == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        data = json.loads(blob_client.download_blob().content_as_text())
    elif file_env == 'OS':
        with open(file_path, 'r') as infile:
            data = json.load(infile)
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")
    return data

def export_string_to_file(text, file_path, file_env='OS'):
    if file_env == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        blob_client.upload_blob(text, overwrite=True)
    elif file_env == 'OS':
        # create directory if it doesn't exist
        directory_path = os.path.dirname(file_path)
        create_directory_if_not_exists(directory_path)
        with open(file_path, 'w') as outfile:
            outfile.write(text)
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")

def export_bytes_to_file(bytes_data, file_path, file_env='OS'):
    if file_env == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        blob_client.upload_blob(bytes_data, overwrite=True)
    elif file_env == 'OS':
        # create directory if it doesn't exist
        directory_path = os.path.dirname(file_path)
        create_directory_if_not_exists(directory_path)
        with open(file_path, 'wb') as outfile:
            outfile.write(bytes_data)
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")

def import_bytes_from_file(file_path, file_env='OS'):
    if file_env == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        bytes_data = blob_client.download_blob().content_as_bytes()
    elif file_env == 'OS':
        with open(file_path, 'rb') as infile:
            bytes_data = infile.read()
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")
    return bytes_data

def import_string_from_file(file_path, file_env='OS'):
    if file_env == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        text = blob_client.download_blob().content_as_text()
    elif file_env == 'OS':
        with open(file_path, 'r') as infile:
            text = infile.read()
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")
    return text

def create_directory_if_not_exists(directory_path, file_env='OS'):
    if file_env == 'OS':
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    elif file_env == 'AZURE':
        # Directories are not used in Azure Blob Storage
        #TODO: add container if doesn't exist
        pass
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")

def create_blob_if_not_exists(container_name, blob_name):
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(container_name)
    
    # Create the container if it does not exist
    try:
        container_client.create_container()
    except ResourceExistsError:
        pass
    
    # Check if the blob exists
    blob_client = container_client.get_blob_client(blob_name)
    try:
        blob_client.get_blob_properties()
        print(f"Blob {blob_name} already exists in container {container_name}.")
    except ResourceNotFoundError:
        # Create an empty blob if it does not exist
        blob_client.upload_blob(b"", overwrite=True)
        print(f"Created blob {blob_name} in container {container_name}.")


def zip_and_delete_files(folder_path, zip_name, file_env='OS'):
    if file_env == 'OS':
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
    elif file_env == 'AZURE':
        # Azure Blob Storage does not have built-in support for zip files.
        # You need to implement your own logic to archive and delete files in Azure Blob Storage.
        # TODO: probably just move the files somewhere else
        pass
    else:
        raise ValueError("Invalid file_env value. Must be 'AZURE' or 'OS'.")

def concatenate_audio_files(input_folder, output_file, file_env="OS"):
    if file_env == "OS":
        audio_files = sorted(os.listdir(input_folder), key=lambda x: int(x.split('.')[0]))

        combined_audio = AudioSegment.empty()

        for audio_file in audio_files:
            audio_path = os.path.join(input_folder, audio_file)
            audio = AudioSegment.from_mp3(audio_path)
            combined_audio += audio

        combined_audio.export(output_file, format="mp3")

    elif file_env == "AZURE":

        blob_service_client = get_blob_service_client()
        input_container = blob_service_client.get_container_client(input_folder)

        combined_audio = AudioSegment.empty()

        for blob in input_container.list_blobs():
            blob_client = input_container.get_blob_client(blob)
            blob_data = blob_client.download_blob()

            with BytesIO(blob_data.readall()) as blob_stream:
                audio = AudioSegment.from_mp3(blob_stream)
                combined_audio += audio

        output_container_name, output_blob_name = output_file.split('/', 1)
        output_container = blob_service_client.get_container_client(output_container_name)
        output_blob_client = output_container.get_blob_client(output_blob_name)

        with BytesIO() as output_stream:
            combined_audio.export(output_stream, format="mp3")
            output_stream.seek(0)
            output_blob_client.upload_blob(output_stream, overwrite=True)

    else:
        raise NotImplementedError("Unsupported file environment")

