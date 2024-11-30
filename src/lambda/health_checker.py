import json
import boto3
import requests
from datetime import datetime
import os
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)

class HealthChecker:
    def __init__(self, table_name: str):
        logger.info(f"Initializing HealthChecker with table {table_name}")
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.ENDPOINTS = [
            {
                "name": "GitHub API",
                "url": "https://api.github.com/zen",
                "expected_status": 200
            },
            {
                "name": "Google",
                "url": "https://www.google.com",
                "expected_status": 200
            }
        ]
        logger.info(f"Configured monitoring for {len(self.ENDPOINTS)} endpoints: {[e['name'] for e in self.ENDPOINTS]}")
    
    def check_single_endpoint(self, endpoint):
        logger.info(f"Starting health check for {endpoint['name']} ({endpoint['url']})")
        start_time = datetime.now()
        try:
            logger.info(f"Sending HTTP request to {endpoint['name']}")
            response = requests.get(
                endpoint["url"],
                timeout=5,
                headers={'User-Agent': 'HealthMonitor/1.0'}
            )
            
            latency = Decimal(str((datetime.now() - start_time).total_seconds() * 1000))
            logger.info(f"Received response from {endpoint['name']}: Status {response.status_code}, Latency {latency}ms")

            is_healthy = response.status_code == endpoint["expected_status"]
            status = "HEALTHY" if is_healthy else "UNHEALTHY"
            
            result = {
                "name": endpoint["name"],
                "url": endpoint["url"],
                "statusCode": response.status_code,
                "latency": latency,
                "timestamp": str(datetime.now()),
                "status": status
            }
            
            logger.info(f"Health check result for {endpoint['name']}: {status} (Status Code: {response.status_code})")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error checking {endpoint['name']}: {str(e)}")
            logger.error(f"Full error details for {endpoint['name']}: {type(e).__name__}: {str(e)}")
            return {
                "name": endpoint["name"],
                "url": endpoint["url"],
                "statusCode": 0,
                "latency": Decimal('0'),
                "timestamp": str(datetime.now()),
                "status": "ERROR",
                "error": f"{type(e).__name__}: {str(e)}"
            }
    
    def store_result(self, result):
        """Store a health check result with detailed logging of the storage operation."""
        try:
            logger.info(f"Attempting to store result for {result['name']} in DynamoDB")
            self.table.put_item(Item=result)
            logger.info(f"Successfully stored result for {result['name']} in DynamoDB")
        except Exception as e:
            logger.error(f"Failed to store results in DynamoDB for {result['name']}")
            logger.error(f"DynamoDB error details: {type(e).__name__}: {str(e)}")
            raise
    
    def check_all_endpoints(self):
        """Check all endpoints with logging of overall progress."""
        logger.info(f"Beginning health checks for {len(self.ENDPOINTS)} endpoints")
        results = []
        
        for i, endpoint in enumerate(self.ENDPOINTS, 1):
            logger.info(f"Processing endpoint {i} of {len(self.ENDPOINTS)}: {endpoint['name']}")
            result = self.check_single_endpoint(endpoint)
            logger.info(f"Storing results for {endpoint['name']}")
            self.store_result(result)
            results.append(result)
            logger.info(f"Completed processing for {endpoint['name']}")
        
        logger.info(f"Completed all health checks. Processed {len(results)} endpoints")
        return results

def lambda_handler(event, context):
    """AWS Lambda handler with comprehensive logging of execution flow."""
    logger.info("Lambda handler started")
    logger.info(f"Event received: {json.dumps(event)}")
    
    try:
        # Get configuration from environment
        table_name = os.environ.get('TABLE_NAME')
        if not table_name:
            logger.error("TABLE_NAME environment variable not found")
            raise ValueError("TABLE_NAME environment variable is required")
            
        logger.info(f"Retrieved table name from environment: {table_name}")
        
        # Create checker and run checks
        checker = HealthChecker(table_name)
        logger.info("Starting health check process")
        results = checker.check_all_endpoints()
        
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Health checks completed",
                "timestamp": str(datetime.now()),
                "results": results
            }, default=str)
        }
        
        logger.info("Health check process completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Critical error in health check execution: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error executing health checks",
                "error": f"{type(e).__name__}: {str(e)}"
            })
        }

if __name__ == "__main__":
    # For local testing
    os.environ['TABLE_NAME'] = 'health-monitor-dev'
    print(lambda_handler({}, None))