variable "project_name" {
  description = "Project name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public Subnet IDs"
  type        = list(string)
}

variable "alb_security_group" {
  description = "ALB Security Group ID"
  type        = string
}

variable "port" {
  description = "Default target group port"
  type        = number
  default     = 8080
}

variable "services" {
  description = "List of microservices"
  type = list(object({
    name         = string
    port         = optional(number, 8080)
    path_pattern = optional(string, "")
  }))
  default = []
}

