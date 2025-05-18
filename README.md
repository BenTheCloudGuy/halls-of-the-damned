# D&D ChatApp: Halls of the Damned

This repository contains the source code, configuration, and campaign data for a dedicated Dungeons & Dragons ChatApp designed to assist the GM and players in recalling campaign-specific lore, characters, and events for the homebrew campaign **"Halls of the Damned"**.

## Purpose

The D&D ChatApp is a custom AI-powered assistant and lore database for the "Halls of the Damned" campaign. It enables the GM and players to:

- Retrieve campaign lore, session summaries, and character information on demand.
- Query campaign documents and receive context-aware responses.
- Generate random encounters, NPCs, and descriptions using campaign-specific data.
- Integrate with external tools (DnDBeyond, Azure, Pinecone, ChromaDB, Ollama, etc.) for advanced features.

## Features

- **Campaign Lore Database:** Markdown files and session logs for all campaign lore, locations, and characters.
- **AI Chatbot:** Custom prompt instructions and integration with LLMs (OpenAI, Ollama) for campaign-aware responses.
- **Document Embedding & Retrieval:** Scripts to extract, chunk, and embed campaign documents for semantic search.
- **DnDBeyond Integration:** Fetch and update character data from DnDBeyond.
- **Azure Blob Storage Integration:** Store and retrieve campaign files and embeddings in the cloud.
- **Dockerized Services:** Compose file for running all required services (Ollama, ChromaDB, RAG service, etc.).
- **Utilities:** Scripts for merging markdown files, extracting images/text from PDFs, and upscaling images.

## Repository Structure

```
dnd-chatapp/
├── functions/                # Python scripts for data extraction, embedding, chatbot, etc.
│   ├── extractFromPDF/       # Extract text/images from campaign PDFs
│   ├── fetch_character_data_api/ # Fetch DnDBeyond character data
│   ├── embedding/            # Embed campaign text into vector DBs
│   ├── knoxrpg-chatbot/      # Chatbot logic and prompt instructions
│   ├── mergeMDfiles/         # Merge markdown files and upload to Azure
│   └── upscaleImages/        # Image upscaling utilities
├── halls-of-the-damned/      # Campaign-specific lore, summaries, and data (Markdown)
│   ├── CHARACTERS/           # Player and NPC character files
│   ├── LOCATIONS/            # Location descriptions and lore
│   ├── CALENDAR.md           # Calendar of Harptos for in-game timekeeping
│   ├── README.md             # Campaign overview and story background
│   └── session_summaries.md # Session-by-session campaign log
├── model_files/              # LLM system prompt and model configuration
├── rag/                      # Retrieval-Augmented Generation (RAG) service and Dockerfile
├── docker-compose.yml        # Compose file for running all services locally
├── requirements.txt          # Python dependencies for RAG service
└── README.md                 # (This file)
```

## Getting Started

1. **Clone the repository** and review the campaign markdown files in `halls-of-the-damned/`.
2. **Set up environment variables** for Azure, OpenAI, Pinecone, and DnDBeyond as needed.
3. **Build and run the stack** using `docker-compose up` to launch all services.
4. **Use the ChatApp** to query campaign lore, generate encounters, and assist with GM tasks.

## Technologies Used

- Python 3.10+
- FastAPI, Uvicorn
- OpenAI, Ollama (LLMs)
- ChromaDB, Pinecone (Vector DBs)
- Azure Blob Storage
- Docker, Docker Compose

## Campaign: Halls of the Damned

This repository is tailored for the "Halls of the Damned" campaign, a homebrew D&D adventure set in the Forgotten Realms. All lore, summaries, and character data are specific to this campaign.

---

*For questions, contributions, or to adapt this ChatApp for your own campaign, please contact the repository owner.*
