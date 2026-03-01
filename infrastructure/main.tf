terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
  backend "s3" {
    key    = "policy-agent/terraform.tfstate"
    region = "us-east-1"
    # bucket set via -backend-config in CI; for local use backend.hcl
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = "procurement-agent"
}
