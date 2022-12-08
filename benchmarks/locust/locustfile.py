from locust import FastHttpUser, task, between

# This needs to be rebuild in docker, and released to docker hub, for changes to take effect
class LocustUser(FastHttpUser):
    wait_time = between(0.1, 0.2)

    @task
    def test(self):
        self.client.get("/")