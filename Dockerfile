FROM python:3.9-slim-buster
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN mkdir /backend
WORKDIR /backend
COPY . /backend
RUN pip install --upgrade pip
RUN pip install -r app/requirements/development.txt
EXPOSE 8000
CMD ["python", "server.py"]
