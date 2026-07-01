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

output "cognito_user_pool_id" {
  description = "Cognito user pool used for TariffGuard operators."
  value       = aws_cognito_user_pool.operators.id
}

output "cognito_client_id" {
  description = "Public Cognito app client ID used by the browser."
  value       = aws_cognito_user_pool_client.dashboard.id
}

output "cognito_authority" {
  description = "OIDC issuer used by the frontend and API Gateway JWT authorizer."
  value       = "https://${aws_cognito_user_pool.operators.endpoint}"
}

output "cognito_domain" {
  description = "Cognito hosted login domain."
  value       = "https://${aws_cognito_user_pool_domain.dashboard.domain}.auth.${var.aws_region}.amazoncognito.com"
}
