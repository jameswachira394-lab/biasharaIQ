locals {
  services_map = length(var.services) > 0 ? {
    for s in var.services : s.name => lookup(var.service_names, s.name, "${var.project_name}-${s.name}")
  } : (
    length(var.service_names) > 0 ? var.service_names : {
      (var.project_name) = var.service_name != "" ? var.service_name : "${var.project_name}-service"
    }
  )
}

resource "aws_sns_topic" "alarms" {
  name = "${var.project_name}-alarms"
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  for_each            = local.services_map
  alarm_name          = "${var.project_name}-${each.key}-high-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Monitors CPU utilization for ECS service ${each.value}"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = each.value
  }
}

resource "aws_cloudwatch_metric_alarm" "memory_high" {
  for_each            = local.services_map
  alarm_name          = "${var.project_name}-${each.key}-high-memory"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Monitors memory utilization for ECS service ${each.value}"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = each.value
  }
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = flatten([
      for idx, svc_name in keys(local.services_map) : [
        {
          type   = "metric"
          x      = (idx % 2) * 12
          y      = floor(idx / 2) * 12
          width  = 12
          height = 6
          properties = {
            metrics = [
              ["AWS/ECS", "CPUUtilization", "ServiceName", local.services_map[svc_name], "ClusterName", var.cluster_name]
            ]
            period = 300
            stat   = "Average"
            region = "us-east-1"
            title  = "${svc_name} CPU Utilization"
          }
        },
        {
          type   = "metric"
          x      = (idx % 2) * 12
          y      = floor(idx / 2) * 12 + 6
          width  = 12
          height = 6
          properties = {
            metrics = [
              ["AWS/ECS", "MemoryUtilization", "ServiceName", local.services_map[svc_name], "ClusterName", var.cluster_name]
            ]
            period = 300
            stat   = "Average"
            region = "us-east-1"
            title  = "${svc_name} Memory Utilization"
          }
        }
      ]
    ])
  })
}

