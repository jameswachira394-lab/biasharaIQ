output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "cluster_id" {
  value = aws_ecs_cluster.main.id
}

output "service_names" {
  description = "Map of service key to ECS service name"
  value       = { for k, v in aws_ecs_service.services : k => v.name }
}

output "service_name" {
  description = "Primary ECS service name"
  value       = length(aws_ecs_service.services) > 0 ? values(aws_ecs_service.services)[0].name : "${var.project_name}-service"
}

output "task_definition_arns" {
  description = "Map of service key to Task Definition ARN"
  value       = { for k, v in aws_ecs_task_definition.services : k => v.arn }
}

output "load_balancer_dns" {
  value = ""
}

