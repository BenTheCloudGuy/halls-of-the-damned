import os
import argparse
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, BlobClient
from io import BytesIO

def merge_markdown_files(input_directory, output_file):
    # Create the target directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as outfile:
        for root, dirs, files in os.walk(input_directory):
            for file in sorted(files):
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n\n")  # Add a newline between files
                    print(f"Merged {file_path}")

def upload_file_to_azure(file_path, container_name, blob_name, account_url, client_id, client_secret, tenant_id):
    # Authenticate using ClientSecretCredential
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Upload the file
    with open(file_path, 'rb') as data:
        blob_client.upload_blob(data, overwrite=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple Markdown files into a single file and upload to Azure Blob Storage")
    parser.add_argument("--input_directory", default="halls-of-the-damned", help="Directory containing Markdown files")
    parser.add_argument("--output_file", default="files/src/halls-of-the-damned/full.txt", help="Output file to save the merged content")
    parser.add_argument("--account_url", default="https://cloudgeekgamingsa01.blob.core.windows.net")
    parser.add_argument("--container_name", default="knoxrpg-chatapp/halls-of-the-damned", help="Name of the container in Azure Storage")
    parser.add_argument("--blob_name", default="full.txt", help="Name of the blob in Azure Storage")
    parser.add_argument("--client_id", default=os.getenv("KNOXRPG_CLIENT_ID"), help="Azure AD Client ID")
    parser.add_argument("--client_secret", default=os.getenv("KNOXRPG_CLIENT_SECRET"), help="Azure AD Client Secret")
    parser.add_argument("--tenant_id", default=os.getenv("KNOXRPG_TENANT_ID"), help="Azure AD Tenant ID")

    args = parser.parse_args()

    merge_markdown_files(args.input_directory, args.output_file)
    upload_file_to_azure(args.output_file, args.container_name, args.blob_name, args.account_url, args.client_id, args.client_secret, args.tenant_id)
