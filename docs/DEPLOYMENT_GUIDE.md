# Deployment Guide — DevOps Assignment (AWS Free Tier)

Production-like Node.js app on EC2 behind Nginx, with CI/CD, monitoring, backups, HTTPS and API Gateway.

**Live endpoints**
| Channel | URL |
|---|---|
| Direct HTTP | http://54.80.171.245/ |
| Direct HTTPS (self-signed) | https://54.80.171.245.nip.io/ |
| API Gateway (trusted TLS) | https://tunjy62f54.execute-api.us-east-1.amazonaws.com/ |

## 1. Infrastructure

| Resource | Value |
|---|---|
| EC2 | `i-0a9df4800e23576b3`, t3.micro, Ubuntu 24.04, us-east-1 |
| Security Group | `sg-0cb01e345e7e5eff7` — 80/443 open, 22 restricted to admin IP |
| IAM instance role | `ec2-app-role` — CloudWatchAgentServerPolicy, S3 read + scoped backup write |
| S3 | `devops-assignment-backups-333888905061` — versioned, all public access blocked |
| API Gateway | HTTP API `devops-assignment-api` (`tunjy62f54`), proxy to EC2 |

## 2. Server layout (on EC2)

- `/opt/app/server.js` — Node app, listens on `:3000`
- `/etc/systemd/system/app.service` — systemd unit (auto-restart, logs to `/var/log/app/app.log`)
- Nginx reverse proxy: `:80` and `:443` (TLS, self-signed cert in `/etc/nginx/ssl/`) → `127.0.0.1:3000`
- CloudWatch agent: config pushes CPU/mem/disk/TCP metrics (`DevOpsAssignment` namespace) and 3 log groups
- `/usr/local/bin/backup-to-s3.sh` + `/etc/cron.d/s3-backup` — daily 02:00 UTC backup of app + logs to S3

## 3. CI/CD pipeline (GitHub Actions)

Trigger: push to `main`. Steps ([.github/workflows/deploy.yml](../.github/workflows/deploy.yml)):

1. Checkout + `node --check server.js` (syntax test)
2. Configure AWS credentials (dedicated `github-actions-ci` IAM user — can *only* open/close SG ingress)
3. Detect runner public IP → **temporarily authorize** it on port 22
4. `scp` app files to EC2 → run `deploy.sh` over SSH
5. Health check: `curl` must return the app page
6. **Always revoke** the runner IP rule (`if: always()`), so port 22 stays closed to the world

Required GitHub secrets: `EC2_HOST`, `EC2_SSH_KEY` (PEM, **LF line endings**), `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

## 4. Monitoring

- Dashboard: CloudWatch → `DevOpsAssignment-Dashboard` (CPU, memory, disk, network, TCP, status checks, live app-log tail)
- Log groups: `/devops-assignment/app`, `/devops-assignment/nginx-access`, `/devops-assignment/nginx-error`
- Alarms: `HighCPU` (>80%/5min), `HighMemory` (>85%/5min), `StatusCheckFailed`

## 5. Rebuilding from scratch (summary)

1. Launch t3.micro Ubuntu 24.04, attach `ec2-app-role`, SG with 80/443 open + 22 from your IP
2. Install nginx + node; create the systemd unit and nginx config above
3. Install CloudWatch agent, apply the agent JSON config, start it
4. Create S3 bucket (versioning on, public access blocked); add the backup script + cron
5. Create the four GitHub secrets; push to `main` — the pipeline deploys and health-checks

## 6. Load testing

See [loadtest/](../loadtest/): Locust staged profile (25→50→100 users), CloudWatch metric collector, and graph generator. Results and analysis in `loadtest/results/` and the final report.

## Troubleshooting notes (real issues hit during setup)

- **`ssh: invalid openssh private key format` in Actions** → the `EC2_SSH_KEY` secret contained CRLF line endings. Fix: re-upload the PEM with LF endings (`gh secret set EC2_SSH_KEY < key.pem` from a Unix-style file).
- **CloudWatch agent `permission denied` tailing nginx logs** → add the `cwagent` user to the `adm` group.
- **Locked out after SSH hardening?** → SG rules are editable from the AWS console/CLI without SSH; re-add your current IP on port 22.
