variable "project" {
  type        = string
  description = "Name of the project for the infrastructure"
  default     = "pss"
}

variable "app_version" {
  type        = string
  description = "Unique version number of the application (Git short hash)"
  default     = "dev"
}

variable "region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones for subnets within the region"
  default     = ["us-east-1a", "us-east-1b"]
}

variable "cidr_block" {
  type        = string
  description = "VPC CIDR block"
  default     = "10.0.0.0/16"
}

variable "backend_port" {
  type        = number
  description = "Backend port container"
  default     = 8000
}

variable "backend_desired_count" {
  type        = number
  description = "Backend desired task count"
  default     = 1
}
