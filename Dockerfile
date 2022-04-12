FROM python:3.7-slim

WORKDIR /app

COPY backend/foodgram_backend/requirements.txt .

RUN pip3 install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir

COPY backend/foodgram_backend/ .

CMD ["gunicorn", "foodgram_backend.wsgi:application", "--bind", "0:8000" ]
