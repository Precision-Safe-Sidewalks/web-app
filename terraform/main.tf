terraform {
  required_version = ">= 1.2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.6"
    }
  }

  backend "s3" {
    bucket = "precision-safe-sidewalks"
    key    = "infrastructure/web-app/pss.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

locals {
  project = var.project
  env     = terraform.workspace == "production" ? "production" : "dev"
}
