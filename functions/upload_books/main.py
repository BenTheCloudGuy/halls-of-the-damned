import os
import argparse
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from tqdm import tqdm

## Upload files to StorageAccount ##
def upload_files_to_azure(directory_path, container_name, account_url, client_id=None, client_secret=None, tenant_id=None):
    
    # Pull credentials from environment variables if not provided
    client_id = client_id or os.getenv("AZURE_CLIENT_ID")
    client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")

    # Authenticate using ClientSecretCredential
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

    # Create a container if it doesn't exist
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container = container_client.create_container()
    except Exception as e:
        print(f"Container already exists: {container_name}")

    # Iterate through the files in the directory
    for root, dirs, files in os.walk(directory_path):
        for file in tqdm(files, desc="Uploading files", unit="file", leave=False):
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=file)

                # Check if the file exists and has not changed
                try:
                    blob_properties = blob_client.get_blob_properties()
                    local_file_size = os.path.getsize(file_path)
                    if blob_properties.size == local_file_size:
                        continue
                except Exception as e:
                    # Blob does not exist
                    pass

                # Upload the file
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload PDF files to Azure Blob Storage")
    parser.add_argument("--directory_path", default="files/books", help="Directory containing PDFs")
    parser.add_argument("--container_name", default="dndsrcbooks", help="Name of the container in Azure Storage")
    parser.add_argument("--account_url", default="https://cloudgeekgamingsa01.blob.core.windows.net")
    parser.add_argument("--client_id", default=os.getenv("KNOXRPG_CLIENT_ID"), help="Azure AD Client ID")
    parser.add_argument("--client_secret", default=os.getenv("KNOXRPG_CLIENT_SECRET"), help="Azure AD Client Secret")
    parser.add_argument("--tenant_id", default=os.getenv("KNOXRPG_TENANT_ID"), help="Azure AD Tenant ID")

    args = parser.parse_args()

    upload_files_to_azure(args.directory_path, args.container_name, args.account_url, args.client_id, args.client_secret, args.tenant_id)