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
# Create state bucket if needed, init with backend
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
TFSTATE_BUCKET="procurement-agent-tfstate-${ACCOUNT_ID}"
aws s3 mb "s3://${TFSTATE_BUCKET}" --region us-east-1 2>/dev/null || true
terraform init -upgrade \
  -backend-config="bucket=${TFSTATE_BUCKET}" \
  -backend-config="key=policy-agent/terraform.tfstate" \
  -backend-config="region=us-east-1"
terraform apply -auto-approve

echo "==> Uploading frontend to S3..."
BUCKET=$(terraform output -raw frontend_bucket)
DISTRIBUTION=$(terraform output -raw cloudfront_distribution_id)
# Use /api (CloudFront proxy to Lambda) for same-origin, avoids 403
echo '{"apiUrl": "/api"}' > "$PROJECT_ROOT/frontend/dist/config.json"
aws s3 sync "$PROJECT_ROOT/frontend/dist" "s3://$BUCKET" --delete

echo "==> Invalidating CloudFront cache..."
aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION" --paths "/config.json" "/index.html"

echo ""
echo "==> Deployment complete!"
echo ""
echo "  App URL (share with anyone): $(terraform output -raw app_url)"
echo ""
echo "  Note: CloudFront may take 1-2 minutes to propagate. Ensure Bedrock model access"
echo "  is enabled in your AWS account (Claude Sonnet 4.6) and credentials are configured."
echo ""
