FROM public.ecr.aws/lambda/python:3.9

# Copy requirements first to leverage Docker caching
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY src/lambda/health_checker.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "health_checker.lambda_handler" ]