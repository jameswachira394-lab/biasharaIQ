variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Unique service/project name (used for all resource names)"
  type        = string
  default     = "biasharaiq"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "port" {
  description = "Container port the default service listens on"
  type        = number
  default     = 8080
}

variable "services" {
  description = "List of microservices to deploy with individual ports and configurations"
  type = list(object({
    name         = string
    port         = optional(number, 8080)
    cpu          = optional(string, "256")
    memory       = optional(string, "512")
    path_pattern = optional(string, "")
  }))
  default = [


    {
      name = "backend"
      port = 8000
    },

    {
      name = "frontend"
      port = 3000
    },


  ]
}

variable "ecr_urls" {
  description = "Map of microservice name to ECR repository image URLs"
  type        = map(string)
  default     = {}
}

