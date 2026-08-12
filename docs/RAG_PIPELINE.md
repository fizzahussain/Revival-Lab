# 🔎 RAG Pipeline

## Ingestion

```text
data/*.txt
   ↓
TextLoader
   ↓
RecursiveCharacterTextSplitter
   ↓
OpenAI text-embedding-3-small
   ↓
Chroma
```

The current splitter uses:

- chunk size: `900`
- overlap: `140`

## Query Path

In full semantic mode:

```text
problem + location + constraints
        ↓
retrieval query
        ↓
OpenAI embedding
        ↓
Chroma similarity retrieval
        ↓
relevant archive evidence
        ↓
LLM synthesis
        ↓
case-file report
```

## Why the Archive Matters

The model is not expected to invent the historical solution set from memory. Retrieval narrows the investigation to curated evidence documents that can be inspected independently.

## Generated Vector Store

`chroma_db/` is generated from the text archive.

It should not be committed because:

- it can be recreated
- it is machine/generated state
- regenerated embeddings may differ across model/provider versions

Rebuild it with:

```bash
python ingest.py --reset
```
