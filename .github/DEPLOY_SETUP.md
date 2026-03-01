# GitHub Actions — Deploy to AWS Setup

The workflow deploys to AWS on every push to `main` or when triggered manually.

## Required: Add GitHub Secrets

**Without these, the workflow will fail with "Credentials could not be loaded".**

1. Go to your repo: **https://github.com/elnamir-ahead/policy-agent**
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add both:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key (e.g. `AKIA...`) |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |

**To create AWS credentials:**
- AWS Console → IAM → Users → your user → Security credentials → Create access key

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
