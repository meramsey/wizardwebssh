FROM python:3.10-slim
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
