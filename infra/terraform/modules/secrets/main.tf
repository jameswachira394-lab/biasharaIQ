resource "aws_secretsmanager_secret" "app" {
  name        = "${var.project_name}-app-secrets"
  kms_key_id  = var.kms_key_arn != "" ? var.kms_key_arn : null
  description = "Application runtime secrets for ${var.project_name}"
}

resource "aws_secretsmanager_secret_version" "app_initial" {
  secret_id     = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    ENVIRONMENT = "production"
    LOG_LEVEL   = "info"
  })
}
