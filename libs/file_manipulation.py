import json
import os
import zipfile
from azure.storage.blob import BlobClient, BlobServiceClient, ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential


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
def export_json_to_file(data, file_path, file_environment='OS'):
    if file_environment == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        
        json_data = json.dumps(data)
        blob_client.upload_blob(json_data, overwrite=True)
    elif file_environment == 'OS':
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile)
    else:
        raise ValueError("Invalid file_environment value. Must be 'AZURE' or 'OS'.")

def import_json_from_file(file_path, file_environment='OS'):
    if file_environment == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        data = json.loads(blob_client.download_blob().content_as_text())
    elif file_environment == 'OS':
        with open(file_path, 'r') as infile:
            data = json.load(infile)
    else:
        raise ValueError("Invalid file_environment value. Must be 'AZURE' or 'OS'.")
    return data

def export_string_to_file(text, file_path, file_environment='OS'):
    if file_environment == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        blob_client.upload_blob(text, overwrite=True)
    elif file_environment == 'OS':
        with open(file_path, 'w') as outfile:
            outfile.write(text)
    else:
        raise ValueError("Invalid file_environment value. Must be 'AZURE' or 'OS'.")

def import_string_from_file(file_path, file_environment='OS'):
    if file_environment == 'AZURE':
        container_name, blob_name = file_path.split('/', 1)
        blob_client = get_blob_client(container_name, blob_name)
        text = blob_client.download_blob().content_as_text()
    elif file_environment == 'OS':
        with open(file_path, 'r') as infile:
            text = infile.read()
    else:
        raise ValueError("Invalid file_environment value. Must be 'AZURE' or 'OS'.")
    return text

def create_directory_if_not_exists(directory_path, file_environment='OS'):
    if file_environment == 'OS':
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    elif file_environment == 'AZURE':
        # Directories are not used in Azure Blob Storage
        #TODO: add container if doesn't exist
        pass
    else:
        raise ValueError("Invalid file_environment value. Must be 'AZURE' or 'OS'.")

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


def zip_and_delete_files(folder_path, zip_name, file_environment='OS'):
    if file_environment == 'OS':
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
    elif file_environment == 'AZURE':
        # Azure Blob Storage does not have built-in support for zip files.
        # You need to implement your own logic to archive and delete files in Azure Blob Storage.
        # TODO: probably just move the files somewhere else
        pass
    else:
        raise ValueError("Invalid file_environment value. Must be 'AZURE' or 'OS'.")



