# Backend configuration for production state persistence
# Configure S3 and DynamoDB state lock when deploying to cloud environments.
# terraform {
#   backend "s3" {
#     bucket         = "biasharaiq-tfstate"
#     key            = "state/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "biasharaiq-tflocks"
#     encrypt        = true
#   }
# }
