output "alb_sg_id" {
  value = aws_security_group.alb.id
}

output "ecs_sg_id" {
  value = aws_security_group.ecs.id
}

output "kms_key_arn" {
  value = aws_kms_key.main.arn
}
