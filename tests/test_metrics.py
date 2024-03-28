import unittest
import requests
from multiprocessing import Process
import os
from scripts.ecs_metrics_exporter import app
import time


def run_mock_server():
    from tests.mock_endpoint import app as mock_app

    mock_app.run(port=5000)


class TestMetricsEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_server_process = Process(target=run_mock_server)
        cls.mock_server_process.start()
        time.sleep(1)

        os.environ["ECS_CONTAINER_METADATA_URI_V4"] = "http://localhost:5000"

        # Set up Flask app for test
        cls.app = app.test_client()
        cls.app.testing = True

    @classmethod
    def tearDownClass(cls):
        cls.mock_server_process.terminate()
        cls.mock_server_process.join()

    def test_metrics_endpoint(self):
        response = self.app.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")

        # ecs_metrics_exporter_success が1であることを確認
        self.assertRegex(content, r"ecs_metrics_exporter_success 1")

        patterns = [
            r'ee_task_cpu_limit{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 0\.5',
            r'ee_task_memory_limit_byte{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 1\.073741824e\+09',
            r'ee_task_pull_started_at_time{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 10\.0',
            r'ee_task_pull_stopped_at_time{[^}]*task_family="taskdef-name-test",[^}]*task_revision="123"[^}]*} 20\.0',
        ]
        for pattern in patterns:
            self.assertRegex(content, pattern)


if __name__ == "__main__":
    unittest.main()
