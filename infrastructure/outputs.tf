output "app_url" {
  description = "Public URL for the Policy Knowledge Agent (share this to run live)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "lambda_function_url" {
  description = "URL for the chat Lambda API"
  value       = aws_lambda_function_url.chat.function_url
}

output "frontend_bucket" {
  description = "S3 bucket for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = aws_cloudfront_distribution.frontend.id
}

output "s3_bucket_name" {
  description = "S3 bucket for knowledge base"
  value       = aws_s3_bucket.knowledge_base.id
}

output "dynamodb_table" {
  description = "DynamoDB table for conversations"
  value       = aws_dynamodb_table.conversations.name
}
