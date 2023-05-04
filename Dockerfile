FROM python:3.11

# Set the working directory in the container
WORKDIR /Whatsapp_GPT

# Copy the requirementdos file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .
# Install dotenv package
RUN pip install python-dotenv

# Expose port 8080 to the host
EXPOSE 8080

# Set the command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]