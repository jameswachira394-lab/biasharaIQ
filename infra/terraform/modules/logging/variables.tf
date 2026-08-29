variable "project_name" {
  description = "Project name"
  type        = string
}

variable "services" {
  description = "List of microservices"
  type = list(object({
    name = string
    port = optional(number, 8080)
  }))
  default = []
}

