resource "aws_cloudwatch_log_group" "default" {
  name              = "/${local.project}/${local.env}"
  retention_in_days = 30

  tags = {
    Project     = local.project
    Environment = local.env
  }
}
