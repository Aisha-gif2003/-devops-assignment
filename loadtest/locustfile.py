"""Load test for the DevOps assignment app.

Staged profile against the EC2 endpoint (via nginx on port 80):
  Stage 1: ramp to 25 users  (warm-up)
  Stage 2: ramp to 50 users  (normal load)
  Stage 3: ramp to 100 users (stress)
  Stage 4: ramp down

Run:
  locust -f locustfile.py --headless --host http://54.80.171.245 \
         --csv results/loadtest --csv-full-history --html results/report.html
"""
from locust import HttpUser, task, between, LoadTestShape


class AppUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(10)
    def home(self):
        self.client.get("/")

    @task(1)
    def home_via_api_gateway_path(self):
        # same origin path; API Gateway is tested separately
        self.client.get("/", name="/ (repeat)")


class StagedShape(LoadTestShape):
    stages = [
        {"duration": 60,  "users": 25,  "spawn_rate": 5},   # warm-up
        {"duration": 150, "users": 50,  "spawn_rate": 5},   # normal
        {"duration": 270, "users": 100, "spawn_rate": 10},  # stress
        {"duration": 300, "users": 10,  "spawn_rate": 10},  # ramp-down
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None
