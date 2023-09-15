resource "aws_lb" "default" {
  name                       = "${local.project}-${local.env}"
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [aws_security_group.default.id]
  subnets                    = aws_subnet.public.*.id
  enable_deletion_protection = false

  tags = {
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_lb_target_group" "default" {
  name        = "${local.project}-${local.env}"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.default.id

  health_check {
    enabled             = true
    path                = "/status/"
    port                = var.backend_port
    matcher             = 200
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.default.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.default.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate_validation.default.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.default.arn
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}
