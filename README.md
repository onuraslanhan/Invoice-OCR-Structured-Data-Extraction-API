# Invoice OCR & Structured Data Extraction API

A containerized REST API built with FastAPI that processes invoice documents (PDFs and images), extracts raw text using Tesseract OCR and Poppler, and parses the extracted text into structured JSON using an LLM via the OpenRouter API, validated against a Pydantic schema.

## 🚀 Live Demo

- **Swagger Documentation:** https://invoice-ocr-structured-data-extraction.onrender.com/docs

## Features

- **Multi-format Support:** Accepts standard image formats (JPEG, PNG) and PDF invoices.
- **Cross-Platform OCR Pipeline:** Tesseract OCR + Poppler (via pdf2image), wrapped in a Docker container for consistent cross-platform behavior.
- **LLM-based Extraction with Schema Validation:** Prompts the LLM to return JSON matching a target schema, then validates the response against a Pydantic model (`Invoice`) — malformed or incomplete LLM output is caught and rejected rather than silently passed through.
- **Fallback-free, Free-tier LLM Access:** Uses OpenRouter's free model routing (`openrouter/free`) to avoid per-provider rate-limit issues encountered with a single vendor's free tier.
- **Graceful Error Handling:** Explicit HTTP status codes (`400` invalid file, `422` unreadable OCR text, `502` LLM/JSON/schema failure) with server-side logging for debugging.

## Tech Stack

- **FastAPI & Uvicorn**
- **Docker**
- **Tesseract OCR & Poppler (via pdf2image)**
- **OpenRouter API (via the `openai` Python client)**
- **Pydantic**

## How It Works

[Upload image/PDF] → [OCR: extract raw text via Tesseract]
→ [LLM: convert raw text to JSON via OpenRouter, prompted with target schema]
→ [Validate JSON against Pydantic Invoice model]
→ [Return validated JSON]


## Local Setup (Docker)

1. Clone the repository:
```bash
   git clone https://github.com/onuraslanhan/Invoice-OCR-Structured-Data-Extraction-API.git
   cd Invoice-OCR-Structured-Data-Extraction-API
```

2. Create a `.env` file in the project root:

OPENROUTER_API_KEY=your_api_key_here


3. Build and run with Docker:
```bash
   docker build -t invoice-ocr-api .
   docker run -p 8000:8000 --env-file .env invoice-ocr-api
```

4. Open the interactive docs:

http://localhost:8000/docs


## Example Request

```bash
curl -X POST "http://localhost:8000/extract-invoice" \
  -F "file=@invoice.jpg"
```

## Example Response

```json
{
  "company": "Grand Name",
  "invoice_number": "52148",
  "date": "01/02/2020",
  "customer": "Dwyane Clark",
  "subtotal": 220.0,
  "tax_rate": "0.00%",
  "items": [
    "Lorem Ipsum Dolor",
    "Pellentesque id neque ligula",
    "Interdum et malesuada fames",
    "Vivamus volutpat faucibus"
  ]
}
```

## Known Limitations

- **Logo/stylized header text has lower OCR accuracy than body text.** Tesseract struggles with stylized fonts and graphic-style headers, occasionally producing unusable text for fields like company name (e.g. a tagline was extracted instead of the actual company name in testing).
- **No schema enforcement at the API level.** Unlike providers that support constrained JSON generation (e.g. Gemini's `response_schema`), OpenRouter's free-tier routing relies on prompt instructions only. This is mitigated by post-hoc Pydantic validation, but malformed output still costs a wasted LLM call before being caught.
- **`openrouter/free` model routing is non-deterministic** — the actual model serving a request can vary between calls, which occasionally produces inconsistent output shapes (encountered and fixed during development: the model initially returned `items` as objects, then as plain strings).
- **Multi-page PDFs only process the first page.**
- **No image preprocessing** (binarization, contrast enhancement, deskewing) is applied before OCR.

## Possible Future Improvements

- Add confidence scores or flag fields the LLM had to infer rather than extract directly
- Image preprocessing pipeline for noisy/rotated scans
- Multi-page PDF support
- Retry with a fixed, pinned model instead of relying on free-tier routing, to reduce output-shape variance
