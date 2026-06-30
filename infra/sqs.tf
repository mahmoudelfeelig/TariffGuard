resource "aws_sqs_queue" "validation_dlq" {
  name = "${local.name}-validation-dlq"
}

resource "aws_sqs_queue" "validation" {
  name                       = "${local.name}-validation"
  visibility_timeout_seconds = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.validation_dlq.arn
    maxReceiveCount     = 3
  })
}
