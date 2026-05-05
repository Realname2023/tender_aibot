FROM python:3.11.14-alpine
WORKDIR /aibot
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && chmod 755 .
COPY . .
ENV TZ Asia/Almaty
CMD ["python3", "-u", "main.py"]