"""
Unit tests for the Web Application and REST API endpoints.
"""
import json
import pytest
from services.web_app import create_app


@pytest.fixture
def wsgi_client():
    app = create_app()

    def make_request(path="/", method="GET"):
        environ = {
            "PATH_INFO": path,
            "REQUEST_METHOD": method,
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "8000",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": None,
            "wsgi.errors": None,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
        }
        response_data = {}

        def start_response(status, headers):
            response_data["status"] = status
            response_data["headers"] = dict(headers)

        body = app(environ, start_response)
        response_data["body"] = b"".join(body)
        return response_data

    return make_request


def test_index_page(wsgi_client):
    res = wsgi_client(path="/", method="GET")
    assert "200" in res["status"]
    assert "text/html" in res["headers"]["Content-Type"]
    assert b"CryptoPulse Tracker" in res["body"]


def test_api_stats(wsgi_client):
    res = wsgi_client(path="/api/stats", method="GET")
    assert "200" in res["status"]
    assert "application/json" in res["headers"]["Content-Type"]
    data = json.loads(res["body"].decode("utf-8"))
    assert "total_coins" in data


def test_api_history(wsgi_client):
    res = wsgi_client(path="/api/history", method="GET")
    assert "200" in res["status"]
    assert "application/json" in res["headers"]["Content-Type"]
    data = json.loads(res["body"].decode("utf-8"))
    assert isinstance(data, list)


def test_404_route(wsgi_client):
    res = wsgi_client(path="/non_existent_route", method="GET")
    assert "404" in res["status"]
