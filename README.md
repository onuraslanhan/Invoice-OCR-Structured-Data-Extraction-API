# Invoice OCR & Structured Data Extraction API

A containerized REST API built with FastAPI that processes invoice documents (PDFs and images), extracts raw text using Tesseract OCR and Poppler, and parses the extracted text into strictly typed JSON via the Gemini API.

## 🚀 Live Demo

- **Swagger Documentation:** https://invoice-ocr-structured-data-extraction.onrender.com/docs

## Features

- **Multi-format Support:** Accepts standard image formats (JPEG, PNG) and PDF invoices.
- **Cross-Platform OCR Pipeline:** Tesseract OCR + Poppler (via pdf2image), wrapped in a Docker container for consistent cross-platform behavior.
- **Structured LLM Extraction:** Enforces typed JSON outputs using Pydantic schemas (`Invoice`, `LineItem`) via the Google GenAI SDK's `response_schema` support.
- **Resilience:** Automatic retry with fallback across multiple Gemini models to handle transient rate-limit and availability errors.

## Tech Stack

- **FastAPI & Uvicorn**
- **Docker**
- **Tesseract OCR & Poppler (via pdf2image)**
- **Google GenAI SDK (Gemini 2.5 Flash)**
- **Pydantic**

## How It Works

[Upload image/PDF] → [OCR: extract raw text via Tesseract]
→ [LLM: convert raw text to structured JSON via Gemini + Pydantic schema]
→ [Return validated JSON]


## Local Setup (Docker)

1. Clone the repository:
```bash
   git clone https://github.com/onuraslanhan/Invoice-OCR-Structured-Data-Extraction-API.git
   cd Invoice-OCR-Structured-Data-Extraction-API
```

2. Create a `.env` file in the project root (see `.env.example`):

GEMINI_API_KEY=your_api_key_here


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
  "date": "01 / 02 / 2020",
  "customer": "Dwyane Clark",
  "subtotal": 220.0,
  "tax_rate": "0.00%",
  "items": [
    { "description": "Lorem Ipsum Dolor" },
    { "description": "Pellentesque id neque ligula" },
    { "description": "Interdum et malesuada fames" },
    { "description": "Vivamus volutpat faucibus" }
  ]
}
```

## Known Limitations

- **Logo/stylized header text** has lower OCR accuracy than body text — Tesseract struggles with stylized fonts and graphic-style headers, sometimes producing unusable output for fields like company name.
- **OCR-tolerant prompting is a trade-off:** instructing the LLM to infer values from noisy OCR text improves accuracy on some fields (e.g. names, dates) but can introduce hallucinated values on others (e.g. company name) when the underlying OCR text is severely corrupted. No confidence scoring is implemented yet to flag low-trust extractions.
- **Multi-page PDFs** only process the first page.
- **No image preprocessing** (binarization, contrast enhancement, deskewing) is applied before OCR — this would likely improve accuracy on real-world (non-template) invoices.

## Possible Future Improvements

- Add confidence scores / flag fields the LLM had to infer rather than extract directly
- Image preprocessing pipeline for noisy/rotated scans
- Multi-page PDF support
- Swap Tesseract for a vision-language model on low-accuracy regions (e.g. logos)
