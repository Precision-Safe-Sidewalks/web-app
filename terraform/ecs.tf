resource "aws_ecs_cluster" "default" {
  name = "${local.project}-${local.env}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${local.project}-${local.env}"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_ecs_cluster_capacity_providers" "default" {
  cluster_name       = aws_ecs_cluster.default.name
  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

resource "aws_ecs_task_definition" "default" {
  family                   = "${local.project}-${local.env}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  execution_role_arn       = data.aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  cpu                      = 1024
  memory                   = 2048

  container_definitions = jsonencode([
    {
      name      = "${local.project}-${local.env}-backend"
      image     = "${data.aws_ecr_repository.default.repository_url}:${var.app_version}"
      cpu       = 1024
      memory    = 2048
      essential = true

      environment = [
        for k, v in local.secrets : { name = k, value = v }
      ]

      portMappings = [
        {
          containerPort = var.backend_port
          hostPort      = var.backend_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group" : aws_cloudwatch_log_group.default.name
          "awslogs-region" : var.region
          "awslogs-stream-prefix" : "backend"
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  tags = {
    Name        = "${local.project}-${local.env}"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_ecs_service" "default" {
  name                   = "${local.project}-${local.env}"
  cluster                = aws_ecs_cluster.default.id
  task_definition        = aws_ecs_task_definition.default.id
  desired_count          = var.backend_desired_count
  launch_type            = "FARGATE"
  force_new_deployment   = true
  enable_execute_command = true

  load_balancer {
    target_group_arn = aws_lb_target_group.default.arn
    container_name   = "${local.project}-${local.env}-backend"
    container_port   = var.backend_port
  }

  network_configuration {
    subnets          = aws_subnet.private.*.id
    security_groups  = [aws_security_group.default.id]
    assign_public_ip = true
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}
