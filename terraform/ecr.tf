data "aws_ecr_repository" "default" {
  name = "pss"
}

data "aws_ecr_repository" "lambda-geocoding" {
  name = "pss-lambda-geocoding"
}
