# Use an official Python 3.10 image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of your application code
COPY ./ /code/

# Run the Uvicorn server on the default Hugging Face port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
