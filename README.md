# DevOps Assignment - AWS Deployment

Node.js app on EC2 with Nginx reverse proxy, deployed automatically via GitHub Actions.

## Architecture
User -> EC2 (Nginx :80 -> Node app :3000), assets/backups in S3, monitoring via CloudWatch.

## Setup
1. EC2 t3.micro (Ubuntu 24.04), provisioned via user-data script
2. Security: SSH restricted to my IP, IAM role with least privilege
3. CI/CD: push to main -> GitHub Actions -> deploy to EC2 -> health check
