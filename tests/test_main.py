import sys
import os
from io import BytesIO
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path so that main.py can import models without backend prefix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app  # This will now work correctly

client = TestClient(app)

def get_mock_openai_success_response():
    class Message:
        def __init__(self, content):
            self.content = content

    class Choice:
        def __init__(self, message):
            self.message = message

    class Response:
        def __init__(self, choices):
            self.choices = choices

    # Valid JSON structure returned by OpenAI
    mock_json = {
        "slides": [
            {"title": "Slide 1", "content": "Content 1"},
            {"title": "Slide 2", "content": "Content 2"},
        ]
    }

    import json
    return Response([Choice(Message(f"```json\n{json.dumps(mock_json)}\n```"))])


def test_valid_topic_default_tone(mocker):
    mocker.patch("main.call_openai_with_retry", return_value=get_mock_openai_success_response())
    mocker.patch("main.create_presentation_from_slides_data", return_value=BytesIO(b"fakeppt"))

    response = client.post("/generate-ppt/", json={"topic": "AI in Education"})
    assert response.status_code == 200


def test_valid_topic_and_tone(mocker):
    mocker.patch("main.call_openai_with_retry", return_value=get_mock_openai_success_response())
    mocker.patch("main.create_presentation_from_slides_data", return_value=BytesIO(b"fakeppt"))

    response = client.post("/generate-ppt/", json={"topic": "Climate Change", "tone": "professional"})
    assert response.status_code == 200


def test_topic_with_special_characters(mocker):
    mocker.patch("main.call_openai_with_retry", return_value=get_mock_openai_success_response())
    mocker.patch("main.create_presentation_from_slides_data", return_value=BytesIO(b"fakeppt"))

    response = client.post("/generate-ppt/", json={"topic": "Climate!@#$%^&*()"})
    assert response.status_code == 200


def test_topic_with_long_text(mocker):
    long_topic = "Impact of climate change on global economies over the past 20 years and the future implications"
    mocker.patch("main.call_openai_with_retry", return_value=get_mock_openai_success_response())
    mocker.patch("main.create_presentation_from_slides_data", return_value=BytesIO(b"fakeppt"))

    response = client.post("/generate-ppt/", json={"topic": long_topic})
    assert response.status_code == 200


def test_valid_with_casual_tone(mocker):
    mocker.patch("main.call_openai_with_retry", return_value=get_mock_openai_success_response())
    mocker.patch("main.create_presentation_from_slides_data", return_value=BytesIO(b"fakeppt"))

    response = client.post("/generate-ppt/", json={"topic": "Quantum computing", "tone": "casual"})
    assert response.status_code == 200


def test_minimal_valid_input(mocker):
    mocker.patch("main.call_openai_with_retry", return_value=get_mock_openai_success_response())
    mocker.patch("main.create_presentation_from_slides_data", return_value=BytesIO(b"fakeppt"))

    response = client.post("/generate-ppt/", json={"topic": "AI"})
    assert response.status_code == 200


def test_invalid_json_response_from_openai(mocker):
    mock_response = get_mock_openai_success_response()
    mock_response.choices[0].message.content = "Invalid JSON"

    mocker.patch("main.call_openai_with_retry", return_value=mock_response)
    mocker.patch("main.create_presentation_from_slides_data", return_value=BytesIO(b"fakeppt"))

    response = client.post("/generate-ppt/", json={"topic": "Invalid JSON"})
    assert response.status_code == 500


def test_openai_call_fails(mocker):
    mocker.patch("main.call_openai_with_retry", side_effect=Exception("OpenAI failure"))

    response = client.post("/generate-ppt/", json={"topic": "Test Failure"})
    assert response.status_code == 500
