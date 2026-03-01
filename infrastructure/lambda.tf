# Lambda function for chat API
# Uses pre-built zip from scripts/build_lambda.sh (includes duckduckgo-search)
resource "aws_lambda_function" "chat" {
  filename         = "${path.module}/build/lambda.zip"
  function_name    = "${var.project_name}-chat"
  role             = aws_iam_role.lambda.arn
  handler          = "lambda_handler.handler"
  source_code_hash = filebase64sha256("${path.module}/build/lambda.zip")
  runtime          = "python3.12"
  timeout          = 60

  environment {
    variables = {
      DYNAMODB_TABLE       = aws_dynamodb_table.conversations.name
      AWS_REGION           = var.aws_region
      ENABLE_WEB_SEARCH    = var.enable_web_search
    }
  }
}

resource "aws_lambda_function_url" "chat" {
  function_name      = aws_lambda_function.chat.function_name
  authorization_type = "NONE"
  cors {
    allow_origins = ["*"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["content-type"]
  }
}
