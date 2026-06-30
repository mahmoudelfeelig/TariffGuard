resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${local.name}-api"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "validation_worker" {
  name              = "/aws/lambda/${local.name}-validation-worker"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "audit_worker" {
  name              = "/aws/lambda/${local.name}-audit-worker"
  retention_in_days = 7
}
