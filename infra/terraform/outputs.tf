output "ecr_repository_url" {
  description = "ECR repository URL for the primary/default service"
  value       = module.ecr.repository_url
}

output "ecr_repository_urls" {
  description = "Map of all microservice ECR repository URLs"
  value       = module.ecr.repository_urls
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name (public endpoint)"
  value       = module.alb.load_balancer_dns
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Primary ECS service name"
  value       = module.ecs.service_name
}

output "ecs_service_names" {
  description = "Map of all ECS microservice names"
  value       = module.ecs.service_names
}

output "log_group_name" {
  description = "CloudWatch log group for the primary service"
  value       = module.logging.log_group_name
}

output "log_group_names" {
  description = "Map of all CloudWatch log groups for microservices"
  value       = module.logging.log_group_names
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "secret_arn" {
  description = "AWS Secrets Manager secret ARN"
  value       = module.secrets.secret_arn
}

