FROM python:3.8.5

WORKDIR /wd

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python"]