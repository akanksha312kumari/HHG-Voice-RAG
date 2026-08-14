# Voice RAG System (HH Goa 2026 - Task 2)

## Task Description
Implementation of a Voice RAG system utilizing a persistent Pinecone index and the Groq LLM API. 

## Current Architecture
The architecture involves a frontend built with Next.js 14 App Router, and a backend built with FastAPI. The backend orchestrates the RAG pipeline via STT, Embedding generation, Pinecone retrieval with 5 distinct chunking strategies stored as metadata, filtering and reranking, and ultimately generation using `gpt-oss-20b` via Groq.

## Repository Structure
- `backend/`: FastAPI application containing pipeline, guardrails, harness, and analytics.
- `frontend/`: Next.js 14 application with UI components.
- `indexing/`: Offline indexing scripts for Pinecone.
- `benchmarks/`: Benchmark test queries and scripts.

## Technology Stack
- Backend: Python 3.11.13, FastAPI, Uvicorn, ONNX Runtime, Pinecone, Groq
- Frontend: Next.js 14 (TypeScript)
- Deployment: Render Native Python

## Environment Variables
See `.env.example` and `frontend/.env.local.example`.

## Local Setup
TODO: Instructions for setting up the environment locally.

## Development Status
Initial skeleton created. No actual functionalities have been implemented yet.
Projected Latency targets (STT to First-Token): 190ms budget. (Note: These are projections, real values to be measured after deployment).
