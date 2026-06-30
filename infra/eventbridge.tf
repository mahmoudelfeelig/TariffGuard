resource "aws_cloudwatch_event_rule" "daily_audit" {
  name                = "${local.name}-daily-audit"
  description         = "Runs the TariffGuard daily audit worker."
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "daily_audit" {
  rule      = aws_cloudwatch_event_rule.daily_audit.name
  target_id = "audit-worker"
  arn       = aws_lambda_function.audit_worker.arn
}

resource "aws_lambda_permission" "daily_audit" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.audit_worker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_audit.arn
}
