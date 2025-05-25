FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR /var/task

# Copy code and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --target .

# Copy the application code
COPY app/ .

# Define the handler (module.function)
CMD ["main.lambda_handler"]
