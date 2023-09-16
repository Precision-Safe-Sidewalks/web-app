data "aws_sqs_queue" "geocoding" {
  name = "${local.project}-geocoding-${local.env}"
}

resource "aws_lambda_function" "geocoding" {
  function_name = "${local.project}-geocoding-${local.env}"
  role          = aws_iam_role.lambda.id
  image_uri     = "${data.aws_ecr_repository.lambda-geocoding.repository_url}:${var.app_version}"

  environment = [
    for k, v in local.secrets : { name = k, value = v }
  ]
}
