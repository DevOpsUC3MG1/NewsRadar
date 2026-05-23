FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY mock_rss_service.py .
EXPOSE 8000
CMD ["python", "mock_rss_service.py", "--host", "0.0.0.0", "--port", "8000"]
