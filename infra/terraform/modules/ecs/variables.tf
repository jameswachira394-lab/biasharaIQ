variable "project_name" {
  description = "Project name"
  type        = string
}

variable "services" {
  description = "List of microservices to deploy"
  type = list(object({
    name   = string
    port   = optional(number, 8080)
    cpu    = optional(string, "256")
    memory = optional(string, "512")
  }))
  default = []
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS tasks"
  type        = list(string)
}

variable "security_group" {
  description = "ECS Security Group ID"
  type        = string
}

variable "alb_security_group" {
  description = "ALB Security Group ID"
  type        = string
}

variable "execution_role" {
  description = "Execution role ARN"
  type        = string
}

variable "task_role" {
  description = "Task role ARN"
  type        = string
}

variable "ecr_repositories" {
  description = "Map of service name to ECR repository URL"
  type        = map(string)
  default     = {}
}

variable "ecr_repository" {
  description = "Fallback single ECR repository URL"
  type        = string
  default     = ""
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
}

variable "secret_arn" {
  description = "Secrets Manager ARN"
  type        = string
  default     = ""
}

variable "log_group_names" {
  description = "Map of service name to Log Group Name"
  type        = map(string)
  default     = {}
}

variable "log_group" {
  description = "Fallback single Log Group Name"
  type        = string
  default     = ""
}

variable "port" {
  description = "Fallback default port number"
  type        = number
  default     = 8080
}

variable "target_group_arns" {
  description = "Map of service name to Target Group ARN"
  type        = map(string)
  default     = {}
}

variable "target_group_arn" {
  description = "Fallback single ALB Target Group ARN"
  type        = string
  default     = ""
}

