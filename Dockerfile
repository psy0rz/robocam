# FROM ultralytics/ultralytics:latest-cpu
FROM ultralytics/ultralytics

WORKDIR /app 
COPY requirements.txt .
RUN pip install -r requirements.txt
