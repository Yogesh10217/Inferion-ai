variable "aws_region" {
  type        = string
  default     = "us-west-2"
  description = "AWS Region for production deployment"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Target deployment environment"
}

variable "cluster_name" {
  type        = string
  default     = "inferion-ai-cluster"
  description = "EKS Kubernetes Cluster Name"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "PostgreSQL Administrator Password"
  default     = "SuperSecretPassword123!"
}
