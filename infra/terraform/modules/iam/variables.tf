variable "project_name" {
  description = "Project name"
  type        = string
}

variable "secret_arn" {
  description = "Secrets Manager ARN"
  type        = string
  default     = ""
}
