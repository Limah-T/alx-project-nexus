FROM python:3.13-slim AS ecommerce_backend

# set working directory
WORKDIR /ecommerce_backend/

# Prevents python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
# Set port the django app to listen to
ENV port=8000

# Install the system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy project files 
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE ${port}

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# For production
# CMD ["gunicorn", "ecommerce_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
