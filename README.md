# 📘 Intelligent Document Question Answering System  
(REST API + AWS + RAG + Gemini + Prompt Engineering)

## 📌 Project Overview

This project is an Intelligent Document Question Answering System that allows users to upload documents (PDF or TXT) and ask questions related to the document content.  
The system retrieves relevant information from the document using Retrieval-Augmented Generation (RAG) and generates a detailed, teacher-style explanation using Gemini AI.

The backend is implemented using AWS REST API and AWS Lambda, following a serverless architecture.

## ✨ Key Features

- Upload PDF or TXT documents
- Ask natural language questions
- Uses Retrieval-Augmented Generation (RAG)
- Uses Prompt Engineering for teacher-style explanations
- Clean, detailed, and academic AI responses
- Built using AWS REST API (not HTTP API)

## 🏗️ System Architecture

Frontend (HTML + JavaScript)  
→ API Gateway (REST API)  
→ AWS Lambda (Python)  
→ Amazon S3 (Document Storage)  
→ Gemini AI (Prompt Engineered Response)  
→ Response back to Frontend

## 🛠️ Technologies Used

### 💻 Frontend
- HTML  
- CSS  
- JavaScript (Fetch API)

### ☁️ Backend (AWS)
- AWS API Gateway (REST API)
- AWS Lambda (Python 3.10)
- AWS S3
- AWS IAM
- AWS CloudWatch

### 🤖 AI & NLP
- Gemini AI (Generative Language API)
- Prompt Engineering
- Retrieval-Augmented Generation (RAG)

## 📂 Supported File Types

- PDF (text-based PDFs only)
- TXT files

⚠️ Scanned PDFs without embedded text are not supported (OCR not implemented).

## 🔄 Application Flow

1. User uploads a document through the frontend.
2. User enters a question related to the document.
3. Frontend sends a POST request to the REST API.
4. AWS Lambda:
   - Stores the document in S3
   - Extracts text from the document
   - Retrieves relevant hints using RAG
   - Sends prompt and context to Gemini AI
5. Gemini AI generates a teacher-style explanation.
6. The response is sent back to the frontend and displayed.

## 🧠 Prompt Engineering Strategy

Prompt engineering is used to make the AI behave like an experienced teacher.  
The prompt guides the AI to:
- Explain concepts clearly and patiently
- Use simple and academic language
- Teach step by step
- Use document content as reference notes
- Expand explanations using general knowledge when required

This ensures the answers are natural, educational, and human-like.

## 📡 API Details (REST API)

Endpoint:  
POST /query

Request Body (JSON):
{
  "filename": "example.pdf",
  "query": "What is YOLO?",
  "filecontent": "<base64-encoded-file>"
}

Response Body (JSON):
{
  "filename": "example.pdf",
  "query": "What is YOLO?",
  "answer": [
    "YOLO is a real-time object detection algorithm...",
    "It works by processing the entire image at once..."
  ]
}

## 🔐 AWS Configuration

IAM Permissions Required:
- AWSLambdaBasicExecutionRole
- AmazonS3FullAccess (or restricted bucket access)

Lambda Environment Variable:
GEMINI_API_KEY = your_gemini_api_key

## ⚠️ Limitations

- Scanned PDFs are not supported
- Depends on Gemini API availability
- Very large documents may reduce retrieval accuracy
- Internet connection is required for AI response

## 🚀 Future Enhancements

- Add OCR support for scanned PDFs
- Support DOCX and PPT files
- Add confidence score for answers
- Enable multi-question chat mode
- Improve frontend UI design

## 🎓 Academic Use Case

This project demonstrates:
- Serverless architecture using AWS
- REST API integration
- RAG-based AI systems
- Prompt engineering techniques
- Real-world AI application design

Suitable for:
- Final year engineering projects
- AI and cloud computing demonstrations
- Viva and technical evaluations

## 👤 Author
ISMAIL SALEEL
