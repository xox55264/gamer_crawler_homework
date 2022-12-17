FROM python:3.6-slim
ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]