variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Name of the project, used for resource naming"
  type        = string
  default     = "health-monitor"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "schedule_expression" {
  description = "How often to run the health checks"
  type        = string
  default     = "rate(5 minutes)"
}