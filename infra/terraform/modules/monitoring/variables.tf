variable "project_name" {
  description = "Project name"
  type        = string
}

variable "cluster_name" {
  description = "ECS Cluster Name"
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

variable "service_names" {
  description = "Map of microservice names to ECS service names"
  type        = map(string)
  default     = {}
}

variable "service_name" {
  description = "Fallback single ECS Service Name"
  type        = string
  default     = ""
}

