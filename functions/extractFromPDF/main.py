import PyPDF2
import fitz
import os
import re
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from io import BytesIO

# Function to extract text from pdf
def pdf_to_text(file_path):
    # Initialize a PDF reader object
    reader = PyPDF2.PdfReader(file_path)
    
    # Extract text from each page
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    return text

# Function to extract images from pdf
def extract_images_from_pdf(pdf_data):
    # Open the PDF file
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

    images = []
    # Iterate through each page
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        page_images = page.get_images(full=True)

        # Iterate through the images on each page
        for img in page_images:
            # Extract the image
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            images.append((image_bytes, image_ext, page_number))

    return images

# Function to upload text to Azure Blob Storage
def upload_text_to_azure(text, blob_client):
    with BytesIO(text.encode('utf-8')) as data:
        blob_client.upload_blob(data, overwrite=True)

# Function to upload images to Azure Blob Storage
def upload_images_to_azure(images, container_client, base_blob_name):
    for idx, (image_bytes, image_ext, page_number) in enumerate(images):
        blob_name = f"{base_blob_name}_page_{page_number+1}_{idx+1}.{image_ext}"
        blob_client = container_client.get_blob_client(blob_name)
        with BytesIO(image_bytes) as data:
            blob_client.upload_blob(data, overwrite=True)

if __name__ == "__main__":
    # Azure Storage Account details
    account_url = "https://cloudgeekgamingsa01.blob.core.windows.net"
    container_name = "dndsrcbooks"
    txt_output_container = "knoxrpg-chatapp/books"
    images_output_container = "knoxrpg-chatapp/images"
    client_id = os.getenv("KNOXRPG_CLIENT_ID")
    client_secret = os.getenv("KNOXRPG_CLIENT_SECRET")
    tenant_id = os.getenv("KNOXRPG_TENANT_ID")

    # Authenticate using ClientSecretCredential
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

    # Get the container client for the source PDFs
    container_client = blob_service_client.get_container_client(container_name)

    # List all PDF blobs in the container
    blob_list = container_client.list_blobs()
    pdf_blobs = [blob for blob in blob_list if blob.name.endswith(".pdf")]

    # Process each PDF blob
    for blob in pdf_blobs:
        blob_client = container_client.get_blob_client(blob)
        pdf_data = blob_client.download_blob().readall()

        # Extract text and images from the PDF
        text = pdf_to_text(BytesIO(pdf_data))
        images = extract_images_from_pdf(BytesIO(pdf_data))

        # Save extracted text to local directory
        local_txt_output_path = os.path.join("files/src/books", f"{blob.name}.txt")
        os.makedirs(os.path.dirname(local_txt_output_path), exist_ok=True)
        with open(local_txt_output_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

        # Save extracted images to local directory
        local_images_output_path = os.path.join("files/src/images", blob.name)
        os.makedirs(local_images_output_path, exist_ok=True)
        for idx, (image_bytes, image_ext, page_number) in enumerate(images):
            image_output_path = os.path.join(local_images_output_path, f"{blob.name}_page_{page_number+1}_{idx+1}.{image_ext}")
            with open(image_output_path, "wb") as image_file:
                image_file.write(image_bytes)

        # Upload extracted text to Azure Blob Storage
        txt_blob_client = blob_service_client.get_blob_client(container=txt_output_container, blob=f"{blob.name}.txt")
        upload_text_to_azure(text, txt_blob_client)

        # Upload extracted images to Azure Blob Storage
        images_container_client = blob_service_client.get_container_client(images_output_container)
        upload_images_to_azure(images, images_container_client, blob.name)

        print(f"Processed {blob.name}")