"""
Unit tests for the ECS metrics exporter.
"""

import unittest
from multiprocessing import Process
import os
import time

from fastapi.testclient import TestClient
import uvicorn

from scripts.ecs_metrics_exporter import app
from tests.mock_endpoint import app as mock_app


def run_mock_server():
    """
    Run the mock server in a separate process.
    """
    uvicorn.run(mock_app, host="127.0.0.1", port=5000)


class TestMetricsEndpoint(unittest.TestCase):
    """
    Test cases for the ECS metrics exporter endpoints.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test class by starting the mock server and initializing the test client.
        """
        cls.mock_server_process = Process(target=run_mock_server)
        cls.mock_server_process.start()
        time.sleep(1)

        os.environ["ECS_CONTAINER_METADATA_URI_V4"] = "http://localhost:5000"

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """
        Tear down the test class by terminating the mock server process.
        """
        cls.mock_server_process.terminate()
        cls.mock_server_process.join()

    def test_metrics_endpoint(self):
        """
        Test the /metrics endpoint.
        """
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn("ecs_metrics_exporter_success 1", content)

        patterns = [
            (r'ee_task_cpu_limit{[^}]*task_family="taskdef-name-test",'
             r'[^}]*task_revision="123"[^}]*} 0\.5'),
            (r'ee_task_memory_limit_byte{[^}]*task_family="taskdef-name-test",'
             r'[^}]*task_revision="123"[^}]*} 1\.073741824e\+09'),
            (r'ee_task_pull_started_at_time{[^}]*task_family="taskdef-name-test",'
             r'[^}]*task_revision="123"[^}]*} 10\.0'),
            (r'ee_task_pull_stopped_at_time{[^}]*task_family="taskdef-name-test",'
             r'[^}]*task_revision="123"[^}]*} 20\.0'),
        ]
        for pattern in patterns:
            self.assertRegex(content, pattern)

    def test_stats_endpoint(self):
        """
        Test the /stats endpoint.
        """
        response = self.client.get("/stats")
        self.assertEqual(response.status_code, 200)

    def test_tasks_endpoint(self):
        """
        Test the /task endpoint.
        """
        response = self.client.get("/task")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
