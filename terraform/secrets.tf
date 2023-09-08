data "aws_secretsmanager_secret" "default" {
  name = "${local.project}/${local.env}/secrets"
}

data "aws_secretsmanager_secret_version" "default" {
  secret_id = data.aws_secretsmanager_secret.default.id
}

locals {
  secrets = jsondecode(data.aws_secretsmanager_secret_version.default.secret_string)
}
