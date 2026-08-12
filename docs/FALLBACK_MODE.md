# 📴 Local Fallback Mode

## Purpose

Revival Lab contains a local retrieval path so the interface can still demonstrate the archive even when OpenAI or the generated Chroma index is unavailable.

## What Still Works

Without a valid API/vector path, the application can still use local keyword/synonym matching to identify relevant archive documents.

That allows users to inspect candidate forgotten solutions and continue using the case-file interface.

## What Changes

The fallback is not equivalent to full semantic RAG:

- retrieval is lexical/heuristic rather than embedding based
- no OpenAI-generated synthesis is available
- structured report sections may contain less detail
- depending on the current source/output parsing, a report panel may show `Evidence not available`

This behavior is documented here intentionally. The GitHub-ready package does **not** modify the application code to hide or change it.

## Full Mode

For the complete vector + LLM path:

1. create `.env` from `.env.example`
2. provide `OPENAI_API_KEY`
3. run `python ingest.py --reset`
4. start the application with `python app.py`
