FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Expose any port if needed, e.g., 8000
# EXPOSE 8000

# Optionally set the connection string at run time:
#   docker run -e POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:5432/db" mcp-postgres
# Start the MCP server; provide the DB DSN via POSTGRES_CONNECTION_STRING
CMD [ "python", "postgres_server.py" ]
