import argparse
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()
    return fallback.replace("_", " ").replace(".txt", "").title()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Revival Lab Chroma vector database from data/*.txt")
    parser.add_argument("--reset", action="store_true", help="Delete the existing chroma_db before rebuilding")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.strip() in {"", "your_api_key_here", "***hidden***"}:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to .env first, then run: python ingest.py --reset"
        )

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    if args.reset and DB_DIR.exists():
        print(f"Resetting vector database: {DB_DIR}")
        shutil.rmtree(DB_DIR)

    documents = []
    for path in sorted(DATA_DIR.glob("*.txt")):
        loader = TextLoader(str(path), encoding="utf-8")
        loaded = loader.load()
        text = path.read_text(encoding="utf-8", errors="ignore")
        title = extract_title(text, path.name)
        for doc in loaded:
            doc.metadata.update({
                "source_file": path.name,
                "title": title,
            })
        documents.extend(loaded)

    if not documents:
        raise RuntimeError("No .txt files found in data/. Add documents before ingesting.")

    print(f"Loaded {len(documents)} source documents from {DATA_DIR}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=140,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} retrievable chunks")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_DIR),
    )

    print(f"Success. Chroma database saved to: {DB_DIR}")
    print("Now run: streamlit run app.py")


if __name__ == "__main__":
    main()
