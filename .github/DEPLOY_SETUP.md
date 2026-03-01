# GitHub Actions — Deploy to AWS Setup

The workflow deploys to AWS on every push to `main` or when triggered manually.

## Required GitHub Secrets

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |

## IAM User Permissions

The IAM user needs permissions for:

- Lambda (create, update, invoke)
- S3 (create buckets, upload objects)
- CloudFront (create distribution, invalidate)
- DynamoDB (create table, read/write)
- IAM (create roles for Lambda)
- Bedrock (invoke model)

**Minimal policy** (or use `AdministratorAccess` for demo):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "s3:*",
        "cloudfront:*",
        "dynamodb:*",
        "iam:*",
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

## Optional: Bedrock API Key

If using Bedrock API key auth instead of IAM, add:

| Secret | Description |
|--------|-------------|
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API key |

Then add to the workflow's Terraform/Lambda env (requires workflow update).

## Manual Deploy

1. Go to **Actions** → **Deploy to AWS**
2. Click **Run workflow** → **Run workflow**
