variable "project_name" {
  description = "Project name"
  type        = string
}

variable "services" {
  description = "List of microservices to create ECR repositories for"
  type = list(object({
    name = string
    port = optional(number, 8080)
  }))
  default = []
}

