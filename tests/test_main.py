import pytest
import httpx
import os
from unittest.mock import MagicMock

# Assuming the FastAPI server runs on localhost:8000
# Adjust if your server runs on a different port or host
BASE_URL = os.getenv("PYTEST_BASE_URL", "http://127.0.0.1:8000")
PPTX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

MOCKED_SLIDES_JSON = '{"slides": [{"title": "Mocked Slide", "bullets": ["Mocked bullet 1", "Mocked bullet 2"]}]}'

@pytest.mark.asyncio
async def test_generate_ppt_valid_topic_default_tone(mocker):
    # Test with a valid topic and default tone (educational)
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": "The History of Python"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_valid_topic_specified_tone(mocker):
    # Test with a valid topic and a specified tone
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": "Quantum Physics Explained", "tone": "formal"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_single_word_topic(mocker):
    # Test with a single word topic
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": "AI"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_long_sentence_topic(mocker):
    # Test with a long sentence topic
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    topic = "An in-depth analysis of the socio-economic impacts of renewable energy adoption in developing nations from 2000 to 2020"
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=45.0) as client: 
        response = await client.post("/generate-ppt/", json={"topic": topic})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_single_word_tone(mocker):
    # Test with a single word tone
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": "Introduction to Machine Learning", "tone": "casual"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

# Negative Test Cases
@pytest.mark.asyncio
async def test_generate_ppt_empty_topic():
    # Test with an empty topic string - No mocking needed, tests FastAPI validation
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": ""})
    assert response.status_code == 422  # Expecting Unprocessable Entity

@pytest.mark.asyncio
async def test_generate_ppt_too_long_topic(mocker):
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)
    
    long_topic = "a" * 1001 
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": long_topic})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_empty_tone(mocker):
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": "Valid Topic", "tone": ""})
    assert response.status_code == 200 
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_too_long_tone(mocker):
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    long_tone = "b" * 101 
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": "Valid Topic", "tone": long_tone})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_topic_with_only_special_chars(mocker):
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [MagicMock()]
    mock_openai_response.choices[0].message = MagicMock()
    mock_openai_response.choices[0].message.content = MOCKED_SLIDES_JSON
    mocker.patch("backend.main.call_openai_with_retry", return_value=mock_openai_response)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.post("/generate-ppt/", json={"topic": "!@#$%^&*()_+"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
