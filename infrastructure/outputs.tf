output "lambda_function_name" {
  description = "Name of the created Lambda function"
  value       = aws_lambda_function.health_checker.function_name
}

output "dynamodb_table_name" {
  description = "Name of the created DynamoDB table"
  value       = aws_dynamodb_table.health_checks.name
}

output "lambda_function_arn" {
  description = "ARN of the created Lambda function"
  value       = aws_lambda_function.health_checker.arn
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.schedule.name
}