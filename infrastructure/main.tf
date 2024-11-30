provider "aws" {
  region = var.aws_region
}

# DynamoDB table to store our health check results
resource "aws_dynamodb_table" "health_checks" {
  name           = "${var.project_name}-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"  # We only pay for what we use
  hash_key       = "name"
  range_key      = "timestamp"

  attribute {
    name = "name"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Container registry for our Docker image
resource "aws_ecr_repository" "health_monitor" {
  name         = "health-monitor"
  force_delete = true  # Makes cleanup easier during development
}

# The Lambda function that runs our health checks
resource "aws_lambda_function" "health_checker" {
  function_name = "${var.project_name}-${var.environment}"
  role         = aws_iam_role.lambda_role.arn
  package_type = "Image"
  image_uri    = "${aws_ecr_repository.health_monitor.repository_url}:latest"
  timeout      = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.health_checks.name
    }
  }
}

# Single IAM role for our Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Single policy that includes all necessary permissions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          aws_dynamodb_table.health_checks.arn,
          "arn:aws:logs:*:*:*"
        ]
      }
    ]
  })
}

# EventBridge rule for scheduled execution
resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "${var.project_name}-schedule-${var.environment}"
  description         = "Schedule for running health checks"
  schedule_expression = var.schedule_expression

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Connect EventBridge to our Lambda function
resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  target_id = "HealthChecker"
  arn       = aws_lambda_function.health_checker.arn
}

# Allow EventBridge to trigger our Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_checker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule.arn
}