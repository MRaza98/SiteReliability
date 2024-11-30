# Service Health Monitor

A serverless service health monitoring system built with AWS Lambda.

## Architecture

<img width="737" alt="image" src="https://github.com/user-attachments/assets/60984123-7cf4-4bcc-b4f1-1a0123be9077">


This system uses:

- AWS Lambda for serverless computation
- DynamoDB for storing health check results
- EventBridge for scheduled execution
- Terraform for infrastructure as code

## Project Structure

```
service-monitor/
├── src/
│   └── lambda/
│       └── health_checker.py
├── infrastructure/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── tests/
│   └── test_health_checker.py
└── README.md
```

## Local Development

1. Set up virtual environment:
```bash
python -m venv site_reliability
source venv/bin/activate

```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Deployment

1. Configure AWS credentials
2. Initialize Terraform:
```bash
cd infrastructure
terraform init
```

3. Deploy:
```bash
terraform apply
```

## Features

- Real-time health monitoring of web services
- Latency tracking
- Historical data storage
- Automated deployment
