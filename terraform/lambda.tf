resource "aws_lambda_function" "geocoding" {
  function_name = "${local.project}-geocoding-${local.env}"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.lambda-geocoding.repository_url}:${var.app_version}"
  timeout       = 300
  memory_size   = 512

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

resource "aws_lambda_function" "pricing_sheet" {
  function_name = "${local.project}-pricing-sheet-${local.env}"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.lambda-pricing-sheet.repository_url}:${var.app_version}"
  timeout       = 300
  memory_size   = 2048

  ephemeral_storage {
    size = 1024
  }

  environment {
    variables = {
      API_KEY      = local.secrets.LAMBDA_API_KEY
      API_BASE_URL = "https://app.bluezoneautomation.com"
    }
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_lambda_function" "project_summary" {
  function_name = "${local.project}-project-summary-${local.env}"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.lambda-project-summary.repository_url}:${var.app_version}"
  timeout       = 300
  memory_size   = 2048

  ephemeral_storage {
    size = 1024
  }

  environment {
    variables = {
      API_KEY      = local.secrets.LAMBDA_API_KEY
      API_BASE_URL = "https://app.bluezoneautomation.com"
    }
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}
