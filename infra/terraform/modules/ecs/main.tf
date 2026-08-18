locals {
  services_map = length(var.services) > 0 ? {
    for s in var.services : s.name => s
  } : {
    (var.project_name) = { name = var.project_name, port = var.port, cpu = "256", memory = "512" }
  }
}

resource "aws_ecs_cluster" "main" {
  name = "${lower(var.project_name)}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Project = var.project_name
  }
}

resource "aws_ecs_task_definition" "services" {
  for_each                 = local.services_map
  family                   = "${lower(var.project_name)}-${each.key}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = coalesce(each.value.cpu, "256")
  memory                   = coalesce(each.value.memory, "512")
  execution_role_arn       = var.execution_role
  task_role_arn            = var.task_role

  container_definitions = jsonencode([
    {
      name      = each.key
      image     = lookup(var.ecr_repositories, each.key, var.ecr_repository != "" ? (endswith(var.ecr_repository, ":latest") ? var.ecr_repository : "${var.ecr_repository}:latest") : "${each.key}:latest")
      essential = true
      portMappings = [
        {
          containerPort = coalesce(each.value.port, var.port)
          hostPort      = coalesce(each.value.port, var.port)
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "SERVICE_NAME"
          value = each.key
        },
        {
          name  = "ROOT_PATH"
          value = contains(["frontend", "web", "ui"], each.key) ? "" : "/${each.key}"
        }
      ]
      secrets = var.secret_arn != "" ? [
        {
          name      = "APP_SECRETS"
          valueFrom = var.secret_arn
        }
      ] : []
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = lookup(var.log_group_names, each.key, var.log_group != "" ? var.log_group : "/ecs/${var.project_name}-${each.key}")
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = each.key
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${coalesce(each.value.port, var.port)}/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Project = var.project_name
    Service = each.key
  }
}

resource "aws_ecs_service" "services" {
  for_each        = local.services_map
  name            = "${lower(var.project_name)}-${each.key}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.services[each.key].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.security_group]
    assign_public_ip = true
  }

  dynamic "load_balancer" {
    for_each = lookup(var.target_group_arns, each.key, var.target_group_arn) != "" ? [1] : []
    content {
      target_group_arn = lookup(var.target_group_arns, each.key, var.target_group_arn)
      container_name   = each.key
      container_port   = coalesce(each.value.port, var.port)
    }
  }

  tags = {
    Project = var.project_name
    Service = each.key
  }
}

resource "aws_appautoscaling_target" "ecs_targets" {
  for_each           = aws_ecs_service.services
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${each.value.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  for_each           = aws_appautoscaling_target.ecs_targets
  name               = "${each.key}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  service_namespace  = each.value.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 75.0
  }
}

