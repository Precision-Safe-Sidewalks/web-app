resource "aws_cloudwatch_event_rule" "hourly" {
  name                = "hourly"
  description         = "Every hour periodic event"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "arcgis_sync" {
  arn  = aws_lambda_function.arcgis_sync.arn
  rule = aws_cloudwatch_event_rule.hourly.name
}

resource "aws_lambda_permission" "arcgis_sync" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeAction"
  function_name = aws_lambda_function.arcgis_sync.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.hourly.arn
}
