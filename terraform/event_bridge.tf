resource "aws_cloudwatch_event_rule" "periodic" {
  name                = "periodic"
  description         = "Periodic task event rule (every hour, 7AM - 7PM, Mon-Fri)"
  schedule_expression = "cron(0 7-19 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "arcgis_sync" {
  arn       = aws_lambda_function.arcgis_sync.arn
  rule      = aws_cloudwatch_event_rule.periodic.name
  target_id = "arcgis_sync"
}

resource "aws_lambda_permission" "arcgis_sync" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeAction"
  function_name = aws_lambda_function.arcgis_sync.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.periodic.arn
}
