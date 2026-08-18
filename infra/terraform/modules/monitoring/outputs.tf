output "log_group_name" {
  value = "/ecs/${var.project_name}"
}

output "sns_topic_arn" {
  value = aws_sns_topic.alarms.arn
}
