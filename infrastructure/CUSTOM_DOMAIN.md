# Custom Domain for Policy Knowledge Agent

Use a custom URL like `https://policy-knowledge.yourdomain.com` instead of the default CloudFront URL.

## Prerequisites

- A domain you own (e.g. `yourdomain.com`)
- DNS hosted in Route 53 or another provider

## Steps

### 1. Request SSL certificate (ACM)

1. Go to [AWS Certificate Manager](https://us-east-1.console.aws.amazon.com/acm/home?region=us-east-1#/certificates) (**us-east-1**)
2. Click **Request certificate**
3. Choose **Request a public certificate**
4. Add your domain: `policy-knowledge.yourdomain.com` (or `*.yourdomain.com` for a wildcard)
5. Choose **DNS validation**
6. Complete validation (add the CNAME record to your DNS)
7. Wait for status **Issued**
8. Copy the **Certificate ARN**

### 2. Deploy with custom domain

**Option A: Terraform variables**

Create `terraform.tfvars`:

```hcl
custom_domain       = "policy-knowledge.yourdomain.com"
acm_certificate_arn = "arn:aws:acm:us-east-1:740315635748:certificate/xxxx-xxxx-xxxx"
```

Then run `terraform apply`.

**Option B: GitHub Actions**

Add repository variables or secrets:
- `TF_VAR_custom_domain` = `policy-knowledge.yourdomain.com`
- `TF_VAR_acm_certificate_arn` = `arn:aws:acm:us-east-1:...`

### 3. Point DNS to CloudFront

After `terraform apply`, get the CloudFront domain:

```bash
terraform output -raw app_url
# e.g. d16rp4uhgi8oz0.cloudfront.net
```

Add a **CNAME** record in your DNS:

| Type | Name | Value |
|------|------|-------|
| CNAME | policy-knowledge | d16rp4uhgi8oz0.cloudfront.net |

(Or use Route 53 alias to the CloudFront distribution.)

### 4. Result

Your app will be available at: **https://policy-knowledge.yourdomain.com**

---

## Without a custom domain

The default URL `https://d16rp4uhgi8oz0.cloudfront.net` works as-is. You cannot change the `cloudfront.net` part—only add a custom domain on top.
