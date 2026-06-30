locals {
  name        = "${var.project_name}-${var.environment}"
  backend_dir = "${path.module}/../backend"
  build_dir   = "${path.module}/.terraform-build/${local.name}"
  package_zip = "${path.module}/.terraform-build/${local.name}.zip"
  packager    = "${path.module}/../scripts/package_lambda.py"

  common_environment = {
    MAIN_TABLE_NAME        = aws_dynamodb_table.main.name
    IDEMPOTENCY_TABLE_NAME = aws_dynamodb_table.idempotency.name
    ENVIRONMENT            = var.environment
    CORS_ORIGIN            = var.cors_origin
  }
}
