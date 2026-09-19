# Invoice OCR & Structured Data Extraction API

A containerized REST API built with FastAPI that processes invoice documents (PDFs and images), extracts raw text using Tesseract OCR and Poppler, and parses the extracted text into strictly typed, structured JSON via the OpenRouter API.

## 🚀 Live Demo

- **Swagger Documentation:** https://invoice-ocr-structured-data-extraction.onrender.com/docs

## Features

- **Multi-Format In-Memory Processing:** Accepts standard image formats (JPEG, PNG) and PDF invoices without writing temporary files to disk.
- **Cross-Platform OCR Pipeline:** Tesseract OCR + Poppler (via pdf2image), encapsulated in a Docker container for consistent cross-platform behavior.
- **Structured LLM Extraction:** Transforms noisy OCR output into strictly validated JSON matching explicit Pydantic schemas (`Invoice`, `LineItem`) using OpenRouter's free-tier LLM models.
- **Optimized Docker Caching:** Layered Dockerfile architecture and targeted `.dockerignore` prevent build context bloat and preserve package caches, slashing cloud deployment times on Render from minutes to seconds.
- **Graceful Error Handling:** Explicit HTTP status codes (`400` invalid files, `422` unreadable OCR text, `502` upstream LLM failure) with integrated logging.

## Tech Stack

- **FastAPI & Uvicorn**
- **Docker**
- **Tesseract OCR & Poppler (via pdf2image)**
- **OpenRouter API (`openai` Python client)**
- **Pydantic**

## How It Works

[Upload image/PDF] → [OCR: extract raw text via Tesseract]
→ [LLM: parse raw text into structured JSON via OpenRouter + Pydantic schema]
→ [Return validated JSON]

## Local Setup (Docker)

1. Clone the repository:
```bash
git clone [https://github.com/onuraslanhan/Invoice-OCR-Structured-Data-Extraction-API.git](https://github.com/onuraslanhan/Invoice-OCR-Structured-Data-Extraction-API.git)
cd Invoice-OCR-Structured-Data-Extraction-API
