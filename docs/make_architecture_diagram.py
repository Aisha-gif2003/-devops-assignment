"""Draw the AWS architecture diagram for the DevOps assignment -> docs/architecture.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.png")

fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 160)
ax.set_ylim(0, 100)
ax.axis("off")

C = {
    "user": "#E8F0FE", "gh": "#F6F8FA", "aws": "#FFF8E7",
    "ec2": "#FDEBD0", "sec": "#FDEDEC", "mon": "#EAF7EA", "s3": "#EAF2E3",
}


def box(x, y, w, h, label, fc, fs=11, bold=False, ec="#555"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal")


def arrow(x1, y1, x2, y2, label="", style="-", color="#333", lx=0, ly=0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=16, lw=1.6, ls=style, color=color))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontsize=9,
                ha="center", color=color,
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))


# ---- Outer AWS boundary
ax.add_patch(FancyBboxPatch((52, 4), 104, 78, boxstyle="round,pad=1",
                            fc=C["aws"], ec="#E8A33D", lw=2))
ax.text(104, 79, "AWS us-east-1 (Free Tier)", fontsize=13, fontweight="bold",
        ha="center", color="#B7791F")

# ---- Users / developer
box(4, 62, 24, 10, "End Users\n(Browser / curl)", C["user"], bold=True)
box(4, 30, 24, 10, "Developer\n(git push)", C["user"], bold=True)

# ---- GitHub
box(4, 10, 34, 14, "GitHub\nrepo: -devops-assignment\nActions: Deploy to EC2", C["gh"], bold=True)

# ---- API Gateway
box(58, 62, 30, 12, "API Gateway (HTTP API)\ndevops-assignment-api\nTLS: AWS-managed cert", "#FDE9F0")

# ---- EC2 group
ax.add_patch(FancyBboxPatch((96, 34), 46, 40, boxstyle="round,pad=0.8",
                            fc=C["ec2"], ec="#C87F2F", lw=1.8))
ax.text(119, 71, "EC2 t3.micro (Ubuntu 24.04)", fontsize=11,
        fontweight="bold", ha="center", color="#8A5A1E")
box(100, 56, 38, 9, "Nginx :80 / :443 (TLS)\nreverse proxy", "white", fs=10)
box(100, 44, 38, 8, "Node.js app :3000\n(systemd service)", "white", fs=10)
box(100, 36, 38, 5, "CloudWatch Agent + daily S3 backup cron", "white", fs=9)

# ---- Security group
box(96, 24, 46, 6,
    "Security Group: 80/443 open · 22 restricted to admin IP", C["sec"], fs=9)

# ---- IAM
box(58, 40, 30, 14,
    "IAM (least privilege)\nec2-app-role: CW agent +\nS3 backup write only\nCI user: SG open/close only",
    C["sec"], fs=9)

# ---- S3
box(58, 22, 30, 12, "S3 (versioned, private)\ndevops-assignment-\nbackups-…", C["s3"], fs=10)

# ---- CloudWatch
box(58, 6, 84, 12,
    "CloudWatch — custom metrics (CPU/mem/disk/TCP) · logs (app, nginx) · dashboard · 3 alarms",
    C["mon"], fs=10)

# ---- Arrows
arrow(28, 68, 58, 68, "HTTPS")                              # users -> apigw
arrow(88, 68, 100, 62, "HTTP proxy", lx=2, ly=2)            # apigw -> nginx
arrow(28, 66, 100, 59, "HTTP/HTTPS direct", ly=-2)          # users -> nginx
arrow(16, 30, 16, 24, "push")                               # dev -> github
arrow(38, 17, 100, 40, "deploy: open SG (runner IP) →\nscp+ssh → health check → close SG",
      style="--", color="#7A3E9D", ly=6)                    # gh -> ec2
arrow(119, 44, 119, 41, "")                                 # node -> agent (implicit)
arrow(100, 38, 88, 30, "nightly tar.gz", style="--", color="#4E7A3A")   # ec2 -> s3
arrow(100, 36, 96, 18, "metrics + logs", style="--", color="#3A7A4E")   # ec2 -> cw

plt.title("DevOps Assignment — AWS Architecture", fontsize=15, fontweight="bold", pad=18)
fig.savefig(OUT, dpi=140, bbox_inches="tight")
print(OUT)
