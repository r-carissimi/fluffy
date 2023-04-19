FROM tensorflow/tensorflow:2.0.3
WORKDIR /app
COPY rest_api .
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python3", "fluffy.py"]

EXPOSE 5000
