import unittest
from fastapi.testclient import TestClient
from multiprocessing import Process
import os
from scripts.ecs_metrics_exporter import app
import time

def run_mock_server():
    from tests.mock_endpoint import app as mock_app
    import uvicorn

    uvicorn.run(mock_app, host="127.0.0.1", port=5000)

class TestMetricsEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_server_process = Process(target=run_mock_server)
        cls.mock_server_process.start()
        time.sleep(1)

        os.environ["ECS_CONTAINER_METADATA_URI_V4"] = "http://localhost:5000"

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.mock_server_process.terminate()
        cls.mock_server_process.join()

    def test_metrics_endpoint(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn("ecs_metrics_exporter_success 1", content)

        patterns = [
            r'ee_task_cpu_limit{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 0\.5',
            r'ee_task_memory_limit_byte{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 1\.073741824e\+09',
            r'ee_task_pull_started_at_time{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 10\.0',
            r'ee_task_pull_stopped_at_time{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 20\.0',
        ]
        for pattern in patterns:
            self.assertRegex(content, pattern)

    def test_stats_endpoint(self):
        response = self.client.get("/stats")
        self.assertEqual(response.status_code, 200)
    
    def test_tasks_endpoint(self):
        response = self.client.get("/task")
        self.assertEqual(response.status_code, 200)
                                   
if __name__ == "__main__":
    unittest.main()
