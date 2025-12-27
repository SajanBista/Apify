FROM python:3.10-slim

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies (Scrapy needs these)
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run the actor
CMD ["python", "-m", "src"]
