resource "aws_vpc" "default" {
  cidr_block           = var.cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${local.project}-${local.env}"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_internet_gateway" "default" {
  vpc_id = aws_vpc.default.id

  tags = {
    Name        = "${local.project}-${local.env}"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_eip" "public" {
  domain = "vpc"

  depends_on = [
    aws_internet_gateway.default,
  ]

  tags = {
    Name        = "${local.project}-${local.env}"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_nat_gateway" "private" {
  allocation_id = aws_eip.public.id
  subnet_id     = element(aws_subnet.public.*.id, 0)

  tags = {
    Name        = "${local.project}-${local.env}-private"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.default.id
  count                   = length(var.availability_zones)
  cidr_block              = cidrsubnet(aws_vpc.default.cidr_block, 8, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = true

  tags = {
    Name        = "${local.project}-${local.env}-public-${count.index}"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_subnet" "private" {
  vpc_id = aws_vpc.default.id
  count  = length(var.availability_zones)
  # FIXME: update to just the length
  cidr_block              = cidrsubnet(aws_vpc.default.cidr_block, 8, (8 * length(var.availability_zones)) + count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = false

  tags = {
    Name        = "${local.project}-${local.env}-private-${count.index}"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.default.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.default.id
  }

  tags = {
    Name        = "${local.project}-${local.env}-public"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = element(aws_subnet.public.*.id, count.index)
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.default.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.private.id
  }

  tags = {
    Name        = "${local.project}-${local.env}-private"
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_route_table_association" "private" {
  count          = length(var.availability_zones)
  subnet_id      = element(aws_subnet.private.*.id, count.index)
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "default" {
  name        = "${local.project}-${local.env}"
  vpc_id      = aws_vpc.default.id
  description = "Web traffic ingress/egress"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = var.backend_port
    to_port     = var.backend_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}

resource "aws_security_group" "db" {
  name        = "${local.project}-${local.env}-db"
  vpc_id      = aws_vpc.default.id
  description = "PostgreSQL database ingress/egress"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project     = local.project
    Environment = local.env
  }
}
