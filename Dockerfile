FROM tiangolo/uvicorn-gunicorn:python3.10

RUN apt update && \
    apt install -y htop libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

# O comando padrão será sobrescrito pelo docker-compose ou EasyPanel
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]