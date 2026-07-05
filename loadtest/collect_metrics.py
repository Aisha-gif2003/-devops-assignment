"""Pull CloudWatch metrics for the load test window and save as CSV.

Usage: python collect_metrics.py <start_iso_utc> <end_iso_utc>
"""
import csv
import subprocess
import json
import sys

INSTANCE = "i-0a9df4800e23576b3"
REGION = "us-east-1"

QUERIES = [
    ("cpu_percent", "AWS/EC2", "CPUUtilization",
     [{"Name": "InstanceId", "Value": INSTANCE}], "Average"),
    ("mem_used_percent", "DevOpsAssignment", "mem_used_percent",
     [{"Name": "InstanceId", "Value": INSTANCE}], "Average"),
    ("network_in_bytes", "AWS/EC2", "NetworkIn",
     [{"Name": "InstanceId", "Value": INSTANCE}], "Sum"),
    ("network_out_bytes", "AWS/EC2", "NetworkOut",
     [{"Name": "InstanceId", "Value": INSTANCE}], "Sum"),
    ("tcp_established", "DevOpsAssignment", "netstat_tcp_established",
     [{"Name": "InstanceId", "Value": INSTANCE}], "Average"),
]


def fetch(namespace, metric, dims, stat, start, end):
    cmd = [
        "aws", "cloudwatch", "get-metric-statistics",
        "--namespace", namespace, "--metric-name", metric,
        "--dimensions", json.dumps(dims),
        "--start-time", start, "--end-time", end,
        "--period", "60", "--statistics", stat,
        "--region", REGION, "--output", "json",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    points = json.loads(out.stdout)["Datapoints"]
    return sorted(points, key=lambda p: p["Timestamp"])


def main():
    start, end = sys.argv[1], sys.argv[2]
    for name, ns, metric, dims, stat in QUERIES:
        rows = fetch(ns, metric, dims, stat, start, end)
        path = f"results/{name}.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", name])
            for p in rows:
                w.writerow([p["Timestamp"], p[stat]])
        print(f"{path}: {len(rows)} datapoints")


if __name__ == "__main__":
    main()
