variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Your domain name (e.g., yourdomain.com)"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ARN of the ACM SSL certificate"
  type        = string
  sensitive   = true
}

variable "rds_host" {
  description = "RDS MySQL endpoint"
  type        = string
  sensitive   = true
}

variable "rds_port" {
  description = "RDS MySQL port"
  type        = string
  default     = "3306"
}

variable "rds_user" {
  description = "RDS MySQL username"
  type        = string
  sensitive   = true
}

variable "rds_password" {
  description = "RDS MySQL password"
  type        = string
  sensitive   = true
}

variable "rds_database" {
  description = "RDS MySQL database name"
  type        = string
  default     = "studentdb"
}

variable "create_route53_record" {
  description = "Create Route 53 record for domain"
  type        = bool
  default     = false
}

variable "route53_zone_name" {
  description = "Route 53 hosted zone name (e.g., yourdomain.com)"
  type        = string
  default     = ""
}
