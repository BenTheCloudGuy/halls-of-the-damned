import os
import argparse
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from openai import OpenAI
import pinecone
from pinecone import Pinecone, ServerlessSpec
import nltk
from io import BytesIO
import re

# Download NLTK data for sentence tokenization
nltk.download('punkt')
nltk.download('punkt_tab')

def embed_text(text, model_name="text-embedding-3-small", max_tokens=8192):
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("KNOXRPG_OAI_KEY"))
    
    # Ensure the text length does not exceed the model's maximum context length
    tokens = text.split()
    if len(tokens) > max_tokens:
        text = " ".join(tokens[:max_tokens])
    
    # Generate embeddings using OpenAI's embedding model
    try:
        response = client.embeddings.create(model=model_name, input=text)
        embeddings = response.data[0].embedding
        return embeddings
    except openai.error.InvalidRequestError as e:
        print(f"Error: {e}")
        return None

def upload_embeddings_to_pinecone(embeddings, index, doc_id, namespace):
    # Upload embeddings to PineconeDB with namespace
    index.upsert([(doc_id, embeddings)], namespace=namespace)

def chunk_text(text, chunk_size=512, overlap=50, max_tokens=8192):
    # Tokenize text into sentences
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    # Create chunks with overlap
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > chunk_size or current_length + sentence_length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-overlap:]
            current_length = len(current_chunk)
        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def sanitize_namespace(namespace):
    # Replace non-ASCII characters with underscores
    return re.sub(r'[^\x20-\x7E]', '_', namespace)

def sanitize_id(vector_id):
    # Replace non-ASCII characters with underscores
    return re.sub(r'[^\x20-\x7E]', '_', vector_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed text and upload embeddings to PineconeDB")
    parser.add_argument("--account_url", default="https://cloudgeekgamingsa01.blob.core.windows.net")
    parser.add_argument("--container_name", default="knoxrpg-chatapp", help="Name of the container in Azure Storage")
    parser.add_argument("--client_id", default=os.getenv("KNOXRPG_CLIENT_ID"), help="Azure AD Client ID")
    parser.add_argument("--client_secret", default=os.getenv("KNOXRPG_CLIENT_SECRET"), help="Azure AD Client Secret")
    parser.add_argument("--tenant_id", default=os.getenv("KNOXRPG_TENANT_ID"), help="Azure AD Tenant ID")
    parser.add_argument("--pinecone_index", default="knoxrpg-chatapp", help="Pinecone index name")

    args = parser.parse_args()

    # Authenticate using ClientSecretCredential
    credential = ClientSecretCredential(args.tenant_id, args.client_id, args.client_secret)
    blob_service_client = BlobServiceClient(account_url=args.account_url, credential=credential)
    container_client = blob_service_client.get_container_client(args.container_name)

    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("KNOXRPG_PINECONE_API"))

    # Use the existing index with the name from the environment variable
    index_name = "knoxrpg-index"
    index = pc.Index(index_name)

    # Process each TXT file in the container
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        if blob.name.endswith('.txt'):
            blob_client = container_client.get_blob_client(blob)
            download_stream = blob_client.download_blob()
            text = download_stream.readall().decode('utf-8')

            # Chunk the text
            chunks = chunk_text(text, max_tokens=8192)

            # Embed and upload each chunk
            namespace = sanitize_namespace(blob.name.split('.')[0])  # Use the sanitized file name (without extension) as the namespace
            for i, chunk in enumerate(chunks):
                embeddings = embed_text(chunk)
                doc_id = sanitize_id(f"{blob.name}_{i}")
                upload_embeddings_to_pinecone(embeddings, index, doc_id, namespace)
