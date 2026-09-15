output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC Identifier"
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.app.repository_url
  description = "ECR Repository URL for container image deployment"
}

output "db_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "PostgreSQL Database Connection Endpoint"
}

output "redis_endpoint" {
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
  description = "Redis Cache Endpoint Address"
}
