locals {
  services_map = length(var.services) > 0 ? {
    for s in var.services : s.name => s
  } : {
    (var.project_name) = { name = var.project_name, port = 8080 }
  }
}

resource "aws_cloudwatch_log_group" "services" {
  for_each          = local.services_map
  name              = length(var.services) > 0 ? "/ecs/${var.project_name}-${each.key}" : "/ecs/${var.project_name}"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${each.key}-log-group"
    Project     = var.project_name
    Service     = each.key
    Environment = "production"
  }
}

