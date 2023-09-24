data "aws_ecr_repository" "default" {
  name = "pss"
}

data "aws_ecr_repository" "lambda-geocoding" {
  name = "pss-lambda-geocoding"
}

data "aws_ecr_repository" "lambda-pricing-sheet" {
  name = "pss-lambda-pricing-sheet"
}
