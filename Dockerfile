FROM python:3.11
COPY .src/python /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "/app/github_action_entrypoint.py"]

