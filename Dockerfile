# Small official Python image; same Python version as the local venv
FROM python:3.10-slim

# All following commands run inside /app in the container
WORKDIR /app

# Install dependencies first so this layer is cached when only app code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code (see .dockerignore for what is excluded)
COPY . .

# Tell the flask CLI which file holds the app
ENV FLASK_APP=hello.py

# The app listens on port 5000 inside the container
EXPOSE 5000

# --host=0.0.0.0 makes the server reachable from outside the container
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
