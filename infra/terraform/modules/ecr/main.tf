locals {
  services_map = length(var.services) > 0 ? {
    for s in var.services : s.name => s
  } : {
    (var.project_name) = { name = var.project_name, port = 8080 }
  }
}

resource "aws_ecr_repository" "repos" {
  for_each             = local.services_map
  name                 = lower(startswith(each.key, var.project_name) ? each.key : "${var.project_name}-${each.key}")
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = var.project_name
    Service = each.key
  }
}

resource "aws_ecr_lifecycle_policy" "policies" {
  for_each   = aws_ecr_repository.repos
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 days of images"
        selection = {
          tagStatus   = "any"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 30
        }
        action = { type = "expire" }
      }
    ]
  })
}

