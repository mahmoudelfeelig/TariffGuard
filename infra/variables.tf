variable "aws_region" {
  description = "AWS region to deploy TariffGuard into."
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Name prefix for all resources."
  type        = string
  default     = "tariffguard"
}

variable "environment" {
  description = "Deployment environment name. /dev/seed is disabled when this is production."
  type        = string
  default     = "demo"
}

variable "cors_origin" {
  description = "Allowed CORS origin for the frontend."
  type        = string
  default     = "*"
}

variable "enable_point_in_time_recovery" {
  description = "Enable DynamoDB point-in-time recovery for production-like deployments."
  type        = bool
  default     = false
}

variable "python_executable" {
  description = "Python 3.12 executable used to build the Lambda package. Use python on Windows or python3 on Linux."
  type        = string
  default     = "python"
}
