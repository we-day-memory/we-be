FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /code
COPY ./ /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]