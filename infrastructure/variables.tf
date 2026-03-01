variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "procurement-agent"
}

variable "enable_web_search" {
  description = "Enable web search when KB doesn't have the answer"
  type        = string
  default     = "1"
}
