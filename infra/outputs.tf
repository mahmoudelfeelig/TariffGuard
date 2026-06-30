output "api_base_url" {
  description = "Base URL for the TariffGuard HTTP API."
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "main_table_name" {
  value = aws_dynamodb_table.main.name
}

output "validation_queue_url" {
  value = aws_sqs_queue.validation.url
}
