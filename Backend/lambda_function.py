import json
import logging
import boto3
import base64
import os
import urllib.request
import urllib.error

# -------------------------------------------------
# LOGGING
# -------------------------------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# -------------------------------------------------
# AWS CLIENTS
# -------------------------------------------------
s3 = boto3.client("s3")
BUCKET_NAME = "<your bucket name>"   # change only if needed

# -------------------------------------------------
# GEMINI CONFIG (ENV VARIABLE REQUIRED)
# -------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.0-flash:generateContent"
)

# -------------------------------------------------
# PDF TEXT EXTRACTION (NO OCR)
# -------------------------------------------------
def extract_text_from_pdf_fallback(file_bytes):
    try:
        text = file_bytes.decode("latin1", errors="ignore")
        text = text.replace("\x00", " ")
        return " ".join(text.split()).lower()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""

# -------------------------------------------------
# SIMPLE RAG (LINE BASED)
# -------------------------------------------------
def rag_retrieve(query, text, max_lines=5):
    query = query.lower()
    lines = text.split(".")
    matches = []

    for line in lines:
        clean = line.strip()
        if query in clean.lower() and len(clean) > 40:
            matches.append(clean)

    if not matches:
        return ["No relevant information found in the content."]

    return matches[:max_lines]

# -------------------------------------------------
# GEMINI ANSWER WITH PROMPT ENGINEERING
# -------------------------------------------------
def generate_gemini_answer(query, context_lines):

    if not GEMINI_API_KEY:
        return [
            "AI service is not configured properly.",
            "Missing Gemini API key."
        ]

    prompt = f"""
You are an experienced teacher explaining concepts to an engineering student.

Your role:
- Teach the concept clearly and patiently
- Explain in your own words
- Expand the explanation beyond the notes
- Make the student understand the idea fully

How to answer:
- Use simple and clear language
- Explain step by step
- Maintain an academic tone

Reference notes for teaching:
- These are partial notes
- Use them only as guidance
- Explain the topic fully in your own words

Notes:
{chr(10).join(context_lines)}

Question:
{query}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        GEMINI_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
            return [ai_text.strip()]  # paragraph-style answer

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return context_lines

# -------------------------------------------------
# LAMBDA HANDLER
# -------------------------------------------------
def lambda_handler(event, context):

    logger.info("Lambda invoked")

    # -----------------------------
    # CORS PREFLIGHT
    # -----------------------------
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }

    # -----------------------------
    # READ REQUEST BODY
    # -----------------------------
    body_raw = event.get("body")
    if not body_raw:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Request body missing"})
        }

    if event.get("isBase64Encoded"):
        body_raw = base64.b64decode(body_raw).decode("utf-8")

    body = json.loads(body_raw)

    query = body.get("query")
    filename = body.get("filename")
    filecontent = body.get("filecontent")

    if not query or not filename or not filecontent:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "error": "query, filename, and filecontent are required"
            })
        }

    # -----------------------------
    # DECODE FILE
    # -----------------------------
    try:
        file_bytes = base64.b64decode(filecontent)
    except Exception:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Invalid base64 file"})
        }

    # -----------------------------
    # UPLOAD FILE TO S3
    # -----------------------------
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=file_bytes
    )

    # -----------------------------
    # TEXT EXTRACTION
    # -----------------------------
    if filename.lower().endswith(".pdf"):
        document_text = extract_text_from_pdf_fallback(file_bytes)
    elif filename.lower().endswith(".txt"):
        document_text = file_bytes.decode("utf-8", errors="ignore").lower()
    else:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "error": "Only PDF and TXT files are supported"
            })
        }

    # -----------------------------
    # RAG
    # -----------------------------
    context_lines = rag_retrieve(query, document_text)

    # -----------------------------
    # AI RESPONSE
    # -----------------------------
    answer_lines = generate_gemini_answer(query, context_lines)

    if not answer_lines:
        answer_lines = context_lines

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({
            "filename": filename,
            "query": query,
            "answer": answer_lines
        })
    }
