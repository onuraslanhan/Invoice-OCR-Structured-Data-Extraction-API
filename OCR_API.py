import asyncio
import json
import os
from pathlib import Path
import sys
from typing import List
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from openai import OpenAI
from pdf2image import convert_from_bytes
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
import pytesseract

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

if sys.platform == "win32":
  pytesseract.pytesseract.tesseract_cmd = (
      r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  )
  POPPLER_PATH = (
      r"C:\Users\Onur_\Downloads\Release-26.07.0-0\poppler-26.07.0\Library\bin"
  )
else:
  POPPLER_PATH = None

app = FastAPI()

# OpenRouter client configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

class Invoice(BaseModel):
    company: str
    invoice_number: str
    date: str
    customer: str
    subtotal: float
    tax_rate: str
    items: List[str]
    
@app.post("/extract-invoice")
async def extract_invoice(file: UploadFile = File(...)):
  try:
    if file.content_type == "application/pdf":
      pages = convert_from_bytes(
          file.file.read(), poppler_path=POPPLER_PATH, dpi=300
      )
      img = pages[0]
    else:
      img = Image.open(file.file)
  except UnidentifiedImageError as e:
    raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")

  raw_text = pytesseract.image_to_string(img)

  if not raw_text.strip():
    raise HTTPException(
        status_code=422, detail="Could not extract any text from the image."
    )

  prompt = f"""You are a professional invoice parser.
Extract the details from the following OCR text and return ONLY a valid JSON object matching this schema:
{{
  "company": "string",
  "invoice_number": "string",
  "date": "string",
  "customer": "string",
  "subtotal": 0.0,
  "tax_rate": "string",
  "items": ["string", "string"]
}}

OCR Text:
{raw_text}
"""

  try:
    print("--> Calling OpenRouter Free API...", flush=True)
    completion = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": (
                    "Return ONLY valid JSON. No markdown backticks, no"
                    " explanation."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    raw_response = completion.choices[0].message.content
    print(f"--> RAW LLM RESPONSE: {raw_response}", flush=True)
    print(f"--> MODEL USED: {completion.model}", flush=True)
  except Exception as e:
    print(f"--> [ERROR] OpenRouter call failed: {e}", flush=True)
    raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

  try:
    parsed = json.loads(raw_response)
  except json.JSONDecodeError as e:
      raise HTTPException(
          status_code=502, detail=f"LLM returned invalid JSON: {raw_response}"
      )

  try:
      validated = Invoice(**parsed)
  except ValidationError as e:
      raise HTTPException(
          status_code=502, detail=f"LLM output did not match schema: {e}"
      )

  return validated.model_dump()