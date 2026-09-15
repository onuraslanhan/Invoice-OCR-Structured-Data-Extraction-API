# Invoice OCR & Structured Data Extraction API

A robust, containerized REST API built with FastAPI that processes invoice documents (PDFs and images), extracts raw text using Poppler and Tesseract OCR, and parses the extracted text into strictly typed JSON schemas via Gemini 3.6-flash.

## 🚀 Live Demo

- **Swagger Documentation:** [https://invoice-ocr-structured-data-extraction.onrender.com/docs](https://invoice-ocr-structured-data-extraction.onrender.com/docs)

## Features

- **Multi-format Support:** Accepts standard image formats (JPEG, PNG) and PDF invoices.
- **Cross-Platform OCR Pipeline:** Automated system dependency management (Poppler, Tesseract) wrapped in a minimal Linux Docker container.
- **Structured LLM Extraction:** Enforces deterministic JSON outputs using Pydantic schemas (`Invoice`, `LineItem`) powered by the `google-genai` SDK.

## Tech Stack

- **FastAPI & Uvicorn**
- **Docker**
- **Tesseract OCR & Poppler (via pdf2image)**
- **Google GenAI SDK (Gemini 3.6-flash)**
- **Pydantic**

## Local Setup (Docker)

1. Clone the repository:
   ```bash
   git clone [https://github.com/onuraslanhan/Invoice-OCR-Structured-Data-Extraction-API.git](https://github.com/onuraslanhan/Invoice-OCR-Structured-Data-Extraction-API.git)
   cd Invoice-OCR-Structured-Data-Extraction-API
