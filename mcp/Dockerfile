FROM python:3.11-slim

COPY requirements.txt .
# Install the MCP‑Server package
RUN pip install -r requirements.txt

# Copy the application code
WORKDIR /app
COPY . .

# Expose the default port used by FastMCP (8000)
EXPOSE 7999

# Run the server
CMD ["fastmcp","run", "main.py","--port","7999","--transport","streamable-http"]
