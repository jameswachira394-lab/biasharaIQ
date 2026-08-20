module "networking" {
  source       = "./modules/networking"
  project_name = var.project_name
}

module "security" {
  source       = "./modules/security"
  project_name = lower(var.project_name)
  vpc_id       = module.networking.vpc_id
}

module "iam" {
  source       = "./modules/iam"
  project_name = lower(var.project_name)
  secret_arn   = module.secrets.secret_arn
}

module "ecr" {
  source       = "./modules/ecr"
  project_name = lower(var.project_name)
  services     = var.services
}

module "secrets" {
  source       = "./modules/secrets"
  project_name = lower(var.project_name)
  kms_key_arn  = module.security.kms_key_arn
}

module "logging" {
  source       = "./modules/logging"
  project_name = lower(var.project_name)
  services     = var.services
}

module "alb" {
  source             = "./modules/alb"
  project_name       = lower(var.project_name)
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  alb_security_group = module.security.alb_sg_id
  port               = var.port
  services           = var.services
}

module "ecs" {
  source             = "./modules/ecs"
  project_name       = lower(var.project_name)
  services           = var.services
  subnet_ids         = module.networking.public_subnet_ids
  security_group     = module.security.ecs_sg_id
  alb_security_group = module.security.alb_sg_id
  execution_role     = module.iam.execution_role_arn
  task_role          = module.iam.task_role_arn
  ecr_repositories   = merge(module.ecr.repository_urls, var.ecr_urls)
  ecr_repository     = module.ecr.repository_url
  aws_region         = var.aws_region
  secret_arn         = module.secrets.secret_arn
  log_group_names    = module.logging.log_group_names
  log_group          = module.logging.log_group_name
  port               = var.port
  target_group_arns  = module.alb.target_group_arns
  target_group_arn   = module.alb.target_group_arn
}

module "monitoring" {
  source        = "./modules/monitoring"
  project_name  = lower(var.project_name)
  cluster_name  = module.ecs.cluster_name
  services      = var.services
  service_names = module.ecs.service_names
  service_name  = module.ecs.service_name
}

