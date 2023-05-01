FROM python:3-alpine

# Create Dir
WORKDIR /app

# Install Deps
COPY requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . .

# Expose Entrypoint
EXPOSE 8080
CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "8080" ]