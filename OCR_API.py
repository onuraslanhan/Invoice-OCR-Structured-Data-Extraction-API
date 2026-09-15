import asyncio
import json
import os
from pathlib import Path
import sys
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from google import genai
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
client = genai.Client()


class LineItem(BaseModel):
  description: str


class Invoice(BaseModel):
  company: str
  invoice_number: str
  date: str
  customer: str
  subtotal: float
  tax_rate: str
  items: List[LineItem]


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
    raise HTTPException(status_code=400, detail=f"Geçersiz görsel: {e}")

  raw_text = pytesseract.image_to_string(img)

  if not raw_text.strip():
    raise HTTPException(
        status_code=422, detail="Could not extract any text from the image."
    )

  prompt = f"""The following text was extracted via OCR and may contain character-recognition errors.
    Use context to infer correct values. The "company" field should be the business/sender name issuing 
    the invoice (usually the first prominent line, not a tagline or slogan).

    Extract the invoice details into structured JSON:

    {raw_text}
    """
  print("--- RAW OCR ---")
  print(raw_text)
  print("--- END ---")

  max_retries = 3
  response = None

  for attempt in range(max_retries):
    try:
      response = client.models.generate_content(
          model="gemini-2.5-flash",
          contents=prompt,
          config={
              "response_mime_type": "application/json",
              "response_schema": Invoice,
          },
      )
      break
    except Exception as e:
      if attempt == max_retries - 1:
        raise HTTPException(
            status_code=502, detail=f"LLM call has failed after retries: {e}"
        )
      await asyncio.sleep(2)

  try:
    parsed = json.loads(response.text)
  except json.JSONDecodeError as e:
    raise HTTPException(
        status_code=502, detail=f"LLM has returned invalid JSON: {e}"
    )

  return parsed