# Security Summary

## Network security
- **Security Group** `sg-0cb01e345e7e5eff7`: only 80 (HTTP) and 443 (HTTPS) open to the internet. SSH (22) is restricted to the administrator's IP; found open to `0.0.0.0/0` during audit and **remediated**. A junk port-0 rule was also removed.
- **CI/CD SSH access** does not require a standing hole: the pipeline temporarily authorizes the GitHub runner's IP on port 22 and revokes it in an `always()` step, so even failed runs clean up.
- App port 3000 is never exposed — only Nginx can reach it via localhost.

## Identity & access (least privilege)
- **EC2 instance role** `ec2-app-role`: `CloudWatchAgentServerPolicy`, `AmazonS3ReadOnlyAccess`, plus a scoped inline policy allowing `s3:PutObject`/`s3:ListBucket` on the backup bucket only. No admin rights on the instance credentials.
- **CI IAM user** `github-actions-ci`: inline policy allowing only `ec2:AuthorizeSecurityGroupIngress`/`RevokeSecurityGroupIngress` on the one deploy SG (+ `DescribeSecurityGroups`). A leaked CI key cannot touch any other resource.
- Secrets (SSH key, AWS keys, host) live in GitHub Actions encrypted secrets, never in the repo.

## Data protection
- S3 backup bucket: **all public access blocked**, **versioning enabled** (ransomware/accidental-delete recovery).
- Backups are created on-instance and uploaded via the instance role — no long-lived credentials on the box.

## Transport security
- HTTPS enabled two ways:
  1. Nginx on 443 with TLS 1.2/1.3 and HSTS (self-signed cert for `54.80.171.245.nip.io` — no owned domain, so a public CA cert on the raw IP is not possible; documented trade-off).
  2. **API Gateway endpoint provides fully trusted TLS** (AWS-managed certificate) in front of the same app.

## Monitoring as a security control
- CloudWatch alarms on CPU, memory and instance status surface anomalies (e.g. crypto-mining compromise shows as sustained CPU).
- Nginx access/error logs and app logs are shipped off-host to CloudWatch Logs — tamper-evident and available even if the instance is lost.

## Known gaps / future improvements
- `devops-cli-user` (the human admin CLI user) has `AdministratorAccess` — should be scoped down or replaced with IAM Identity Center + MFA.
- Self-signed cert on the direct endpoint; a real domain + ACM/Let's Encrypt would remove browser warnings.
- No WAF/rate limiting; API Gateway throttling could be enabled.
- SSH could be eliminated entirely by moving deploys to AWS SSM Run Command.
