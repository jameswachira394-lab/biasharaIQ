locals {
  services_map = length(var.services) > 0 ? {
    for s in var.services : s.name => s
  } : {
    (var.project_name) = { name = var.project_name, port = var.port, path_pattern = "" }
  }

  is_multi = length(local.services_map) > 1

  # Sorting: put frontend/web/ui last so specific service paths take priority
  non_frontend = [for s in var.services : s if !contains(["frontend", "web", "ui"], s.name)]
  frontend     = [for s in var.services : s if contains(["frontend", "web", "ui"], s.name)]
  routing_svcs = concat(local.non_frontend, local.frontend)
}

resource "aws_lb" "main" {
  name               = substr("${lower(var.project_name)}-alb", 0, 32)
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group]
  subnets            = var.public_subnet_ids

  tags = {
    Name    = "${var.project_name}-alb"
    Project = var.project_name
  }
}

resource "aws_lb_target_group" "services" {
  for_each    = local.services_map
  name_prefix = substr(replace(replace(lower(each.key), "-", ""), "_", ""), 0, 6)
  port        = coalesce(each.value.port, var.port)
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 5
    timeout             = 5
    interval            = 30
    matcher             = "200-399"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name    = "${var.project_name}-${each.key}-tg"
    Project = var.project_name
    Service = each.key
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = local.is_multi ? "fixed-response" : "forward"
    target_group_arn = local.is_multi ? null : values(aws_lb_target_group.services)[0].arn

    dynamic "fixed_response" {
      for_each = local.is_multi ? [1] : []
      content {
        content_type = "text/plain"
        message_body = "Not found"
        status_code  = "404"
      }
    }
  }
}

resource "aws_lb_listener_rule" "services" {
  for_each     = local.is_multi ? { for idx, s in local.routing_svcs : s.name => { svc = s, priority = idx + 10 } } : {}
  listener_arn = aws_lb_listener.http.arn
  priority     = each.value.priority

  condition {
    path_pattern {
      values = contains(["frontend", "web", "ui"], each.key) ? ["/*"] : (
        each.value.svc.path_pattern != "" ? [each.value.svc.path_pattern] : ["/${each.key}/*", "/${each.key}"]
      )
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.services[each.key].arn
  }
}

