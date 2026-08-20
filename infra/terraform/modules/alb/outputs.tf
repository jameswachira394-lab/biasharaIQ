output "load_balancer_dns" {
  value = aws_lb.main.dns_name
}

output "target_group_arns" {
  description = "Map of service name to target group ARN"
  value       = { for k, v in aws_lb_target_group.services : k => v.arn }
}

output "target_group_arn" {
  description = "Primary target group ARN"
  value       = length(aws_lb_target_group.services) > 0 ? values(aws_lb_target_group.services)[0].arn : ""
}

output "alb_arn" {
  value = aws_lb.main.arn
}

