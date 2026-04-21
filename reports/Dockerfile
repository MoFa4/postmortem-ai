FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# 1️⃣ Install dependencies DIRECTLY (no requirements.txt)
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.27.0 \
    jinja2==3.1.2 \
    aiofiles==23.2.1 \
    requests==2.31.0

# 2️⃣ VERIFY installation during build
RUN python -c "import requests, fastapi, jinja2, aiofiles; print('✅ ALL DEPENDENCIES VERIFIED')"

# 3️⃣ Copy app code
COPY src/ ./src/
COPY static/ ./static/
RUN mkdir -p ./reports

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]