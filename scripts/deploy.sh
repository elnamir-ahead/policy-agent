#!/bin/bash
# Deploy Policy Knowledge Agent to AWS
# Prerequisites: AWS CLI, Terraform, Node.js, Python
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRA_DIR="$PROJECT_ROOT/infrastructure"

echo "==> Building Lambda package..."
"$SCRIPT_DIR/build_lambda.sh"

echo "==> Building frontend..."
"$SCRIPT_DIR/build_frontend.sh"

echo "==> Deploying infrastructure..."
cd "$INFRA_DIR"
terraform init -upgrade
terraform apply -auto-approve

echo "==> Uploading frontend to S3..."
BUCKET=$(terraform output -raw frontend_bucket)
API_URL=$(terraform output -raw lambda_function_url)
# Inject config.json with API URL (--delete would remove Terraform's config, so we add it to dist)
echo "{\"apiUrl\": \"$API_URL\"}" > "$PROJECT_ROOT/frontend/dist/config.json"
aws s3 sync "$PROJECT_ROOT/frontend/dist" "s3://$BUCKET" --delete

echo ""
echo "==> Deployment complete!"
echo ""
echo "  App URL (share with anyone): $(terraform output -raw app_url)"
echo ""
echo "  Note: CloudFront may take 1-2 minutes to propagate. Ensure Bedrock model access"
echo "  is enabled in your AWS account (Claude Sonnet 4.6) and credentials are configured."
echo ""
