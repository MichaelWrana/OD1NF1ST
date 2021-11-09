FROM python:3.8-slim

RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN mkdir /app
COPY . /app/
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 8572
CMD ["python", "-m", "odf.web"]
