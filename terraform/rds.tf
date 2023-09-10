resource "aws_db_instance" "primary" {
  identifier                   = "${local.project}-${local.env}-primary"
  allocated_storage            = 50
  max_allocated_storage        = 500
  db_name                      = "pss"
  engine                       = "postgres"
  engine_version               = "14.7"
  auto_minor_version_upgrade   = false
  instance_class               = "db.t3.micro"
  multi_az                     = false
  username                     = local.secrets.DB_USER
  password                     = local.secrets.DB_PASSWORD
  deletion_protection          = true
  performance_insights_enabled = true
  backup_retention_period      = 7
  db_subnet_group_name         = aws_db_subnet_group.public.name
  publicly_accessible          = true
  skip_final_snapshot          = true
  apply_immediately            = false

  vpc_security_group_ids = [
    aws_security_group.db.id,
  ]

  tags = {
    Name        = "${local.project}-${local.env}-primary"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_db_subnet_group" "public" {
  name       = "${local.project}-${local.env}"
  subnet_ids = aws_subnet.public.*.id

  tags = {
    Project     = local.project
    Environment = local.env
  }
}
