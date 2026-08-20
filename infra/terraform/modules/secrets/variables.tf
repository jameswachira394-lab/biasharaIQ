variable "project_name" {
  description = "Project name"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN"
  type        = string
  default     = ""
}
