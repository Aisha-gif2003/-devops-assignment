"""Generate load test graphs from Locust CSV history + CloudWatch CSVs.

Outputs PNG charts into results/graphs/.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
G = os.path.join(R, "graphs")
os.makedirs(G, exist_ok=True)

hist = pd.read_csv(f"{R}/loadtest_stats_history.csv")
agg = hist[hist["Name"] == "Aggregated"].copy()
agg["t"] = pd.to_datetime(agg["Timestamp"], unit="s")
agg["elapsed_min"] = (agg["Timestamp"] - agg["Timestamp"].min()) / 60


def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"{G}/{name}.png", dpi=120)
    plt.close(fig)
    print(f"graphs/{name}.png")


# 1. Users + throughput
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(agg["elapsed_min"], agg["User Count"], color="tab:blue", label="Users")
ax1.set_xlabel("Elapsed (min)")
ax1.set_ylabel("Concurrent users", color="tab:blue")
ax2 = ax1.twinx()
ax2.plot(agg["elapsed_min"], agg["Requests/s"], color="tab:green", label="Requests/s")
ax2.set_ylabel("Requests/s (throughput)", color="tab:green")
ax1.set_title("Concurrent Users vs Throughput")
save(fig, "01_users_throughput")

# 2. Response time percentiles
fig, ax = plt.subplots(figsize=(10, 5))
for col, lbl in [("50%", "p50 (median)"), ("95%", "p95"), ("99%", "p99")]:
    if col in agg.columns:
        ax.plot(agg["elapsed_min"], pd.to_numeric(agg[col], errors="coerce"), label=lbl)
ax.set_xlabel("Elapsed (min)")
ax.set_ylabel("Response time (ms)")
ax.set_title("Response Time Percentiles")
ax.legend()
save(fig, "02_response_times")

# 3. Error rate
fig, ax = plt.subplots(figsize=(10, 5))
total = agg["Total Request Count"].diff().fillna(0)
fails = agg["Total Failure Count"].diff().fillna(0)
rate = (fails / total.replace(0, 1)) * 100
ax.plot(agg["elapsed_min"], rate, color="tab:red")
ax.set_xlabel("Elapsed (min)")
ax.set_ylabel("Error rate (%)")
ax.set_title("Error Rate Over Time")
ax.set_ylim(bottom=0)
save(fig, "03_error_rate")

# 4. CloudWatch: CPU + memory
def cw(name):
    p = f"{R}/{name}.csv"
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    if df.empty:
        return None
    df["t"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("t")


cpu, mem = cw("cpu_percent"), cw("mem_used_percent")
if cpu is not None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(cpu["t"], cpu["cpu_percent"], label="CPU %", color="tab:orange")
    if mem is not None:
        ax.plot(mem["t"], mem["mem_used_percent"], label="Memory %", color="tab:purple")
    ax.set_ylabel("Utilization (%)")
    ax.set_title("EC2 CPU & Memory During Load Test (CloudWatch)")
    ax.legend()
    fig.autofmt_xdate()
    save(fig, "04_cpu_memory")

net_in, net_out = cw("network_in_bytes"), cw("network_out_bytes")
if net_in is not None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(net_in["t"], net_in["network_in_bytes"] / 1e6, label="Network In (MB/min)")
    if net_out is not None:
        ax.plot(net_out["t"], net_out["network_out_bytes"] / 1e6, label="Network Out (MB/min)")
    ax.set_ylabel("MB per minute")
    ax.set_title("EC2 Network Traffic During Load Test (CloudWatch)")
    ax.legend()
    fig.autofmt_xdate()
    save(fig, "05_network")

# Summary table to console
stats = pd.read_csv(f"{R}/loadtest_stats.csv")
print("\n--- Aggregated summary ---")
print(stats[stats["Name"] == "Aggregated"].T.to_string())
