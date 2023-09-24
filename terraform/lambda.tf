data "aws_sqs_queue" "geocoding" {
  name = "${local.project}-geocoding-${local.env}"
}

resource "aws_lambda_function" "geocoding" {
  function_name = "${local.project}-geocoding-${local.env}"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.lambda-geocoding.repository_url}:${var.app_version}"

  environment {
    variables = {
      DB_HOST             = local.secrets.DB_HOST
      DB_USER             = local.secrets.DB_USER
      DB_PASSWORD         = local.secrets.DB_PASSWORD
      DB_NAME             = local.secrets.DB_NAME
      MAPBOX_ACCESS_TOKEN = local.secrets.MAPBOX_ACCESS_TOKEN
    }
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_lambda_event_source_mapping" "geocoding" {
  event_source_arn = data.aws_sqs_queue.geocoding.arn
  function_name    = aws_lambda_function.geocoding.function_name
  batch_size       = 1
}

resource "aws_lambda_function" "pricing_sheet" {
  function_name = "${local.project}-pricing-sheet-${local.env}"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.lambda-pricing-sheet.repository_url}:${var.app_version}"

  environment {
    variables = {
      DB_HOST     = local.secrets.DB_HOST
      DB_USER     = local.secrets.DB_USER
      DB_PASSWORD = local.secrets.DB_PASSWORD
      DB_NAME     = local.secrets.DB_NAME
    }
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}
