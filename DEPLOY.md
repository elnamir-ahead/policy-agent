# Deploy Policy Knowledge Agent to AWS

Deploy the agent so **anyone can run it live** from your AWS account.

## Prerequisites

- **AWS CLI** configured (`aws configure` or env vars)
- **Terraform** >= 1.5
- **Node.js** 18+ (for frontend build)
- **Python** 3.9+ (for Lambda build)
- **Bedrock access** — enable Claude Sonnet 4.6 in [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/) → Model access

## Quick Deploy

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

This will:
1. Build Lambda (with duckduckgo-search for web search)
2. Build frontend
3. Deploy Terraform (Lambda, S3, CloudFront, DynamoDB)
4. Upload frontend to S3

## Output

After deploy, you'll see:

```
App URL (share with anyone): https://xxxxx.cloudfront.net
```

Share that URL — anyone can use the agent. No login required (demo mode).

## Manual Steps (if deploy script fails)

```bash
# 1. Build Lambda
./scripts/build_lambda.sh

# 2. Build frontend
./scripts/build_frontend.sh

# 3. Deploy infrastructure
cd infrastructure
terraform init
terraform apply

# 4. Upload frontend
aws s3 sync frontend/dist s3://$(terraform output -raw frontend_bucket) --delete
```

## AWS Resources Created

| Resource | Purpose |
|----------|---------|
| Lambda | Chat API (Bedrock + policy logic) |
| Lambda Function URL | Public API endpoint |
| S3 (frontend) | Static site hosting |
| CloudFront | CDN + HTTPS |
| DynamoDB | Conversation state (optional) |
| S3 (knowledge base) | Policy docs (for future RAG) |

## Environment Variables (Lambda)

Set via Terraform `variables.tf`:

- `enable_web_search` — `1` to enable web search when KB doesn't have the answer

For Bedrock API key auth, add to Lambda env in Terraform:
- `AWS_BEARER_TOKEN_BEDROCK` — (sensitive) Bedrock API key

## Cost Estimate (Demo / Low Traffic)

- Bedrock: ~$5–20/month (100–500 requests)
- Lambda: < $1
- CloudFront: < $5
- S3: < $1
- **Total: ~$10–30/month**

## Destroy

```bash
cd infrastructure
terraform destroy
```
