import pytest
from fastapi.testclient import TestClient # Import TestClient
from unittest.mock import MagicMock, patch
from io import BytesIO # Needed for mocking BytesIO return

# Import your FastAPI app instance directly
from backend.main import app # Assuming your FastAPI app instance is named 'app' in backend/main.py

# No longer need BASE_URL for in-process testing
# BASE_URL = os.getenv("PYTEST_BASE_URL", "http://127.0.0.1:8000")
PPTX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

# Consistent mocked OpenAI response for successful PPT generation
MOCKED_SLIDES_JSON = '{"slides": [{"title": "Mocked Slide", "bullets": ["Mocked bullet 1", "Mocked bullet 2"]}]}'

def get_mock_openai_success_response():
    """Helper to create a consistent mock OpenAI success response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = MOCKED_SLIDES_JSON
    return mock_response

# Fixture to create a TestClient for your FastAPI application
@pytest.fixture(scope="module") # Module scope for efficiency, as the app instance doesn't change
def client():
    """Provides a TestClient instance for the FastAPI application."""
    # The 'with' statement ensures lifespan events (like Redis init) are handled
    with TestClient(app) as test_client:
        yield test_client

# --- Positive Test Cases ---

@pytest.mark.asyncio
async def test_generate_ppt_valid_topic_default_tone(mocker, client):
    """
    Test with a valid topic and default tone (educational).
    Mocks the OpenAI call and PPT creation to ensure predictable behavior.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry", # Patch the function where it's *used* (in main.py)
        return_value=get_mock_openai_success_response()
    )
    
    mocker.patch(
        "backend.main.create_presentation_from_slides_data", # Patch the function where it's *used* (in main.py)
        return_value=BytesIO(b"mocked ppt content") # Return a dummy BytesIO object
    )

    response = client.post("/generate-ppt/", json={"topic": "The History of Python"})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content" # Assert the mocked content

@pytest.mark.asyncio
async def test_generate_ppt_valid_topic_specified_tone(mocker, client):
    """
    Test with a valid topic and a specified tone.
    Mocks the OpenAI call and PPT creation.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"mocked ppt content")
    )

    response = client.post("/generate-ppt/", json={"topic": "Quantum Physics Explained", "tone": "formal"})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content"

@pytest.mark.asyncio
async def test_generate_ppt_single_word_topic(mocker, client):
    """
    Test with a single word topic.
    Mocks the OpenAI call and PPT creation.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"mocked ppt content")
    )

    response = client.post("/generate-ppt/", json={"topic": "AI"})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content"

@pytest.mark.asyncio
async def test_generate_ppt_long_sentence_topic(mocker, client):
    """
    Test with a long sentence topic.
    Mocks the OpenAI call and PPT creation.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"mocked ppt content")
    )

    topic = "An in-depth analysis of the socio-economic impacts of renewable energy adoption in developing nations from 2000 to 2020"
    response = client.post("/generate-ppt/", json={"topic": topic})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content"

@pytest.mark.asyncio
async def test_generate_ppt_single_word_tone(mocker, client):
    """
    Test with a single word tone.
    Mocks the OpenAI call and PPT creation.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"mocked ppt content")
    )

    response = client.post("/generate-ppt/", json={"topic": "Introduction to Machine Learning", "tone": "casual"})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content"

@pytest.mark.asyncio
async def test_generate_ppt_topic_with_special_chars(mocker, client):
    """
    Test with a topic containing only special characters.
    Mocks the OpenAI call and PPT creation.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"mocked ppt content")
    )

    response = client.post("/generate-ppt/", json={"topic": "!@#$%^&*()_+"})
    
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content"

# --- Negative Test Cases ---

@pytest.mark.asyncio
async def test_generate_ppt_empty_topic(client):
    """
    Test with an empty topic string.
    Expects a 422 Unprocessable Entity due to FastAPI validation.
    """
    response = client.post("/generate-ppt/", json={"topic": ""})
    
    assert response.status_code == 422
    assert "detail" in response.json()
    # Assert that one of the expected Pydantic error types is present
    assert any(err.get("type") == "string_too_short" for err in response.json()["detail"])


@pytest.mark.asyncio
async def test_generate_ppt_missing_topic(client):
    """
    Test without providing the 'topic' field.
    Expects a 422 Unprocessable Entity due to FastAPI validation.
    """
    response = client.post("/generate-ppt/", json={}) # Missing 'topic'
    
    assert response.status_code == 422
    assert "detail" in response.json()
    # Assert that the expected Pydantic error type is present
    assert any(err.get("type") == "missing" for err in response.json()["detail"])


@pytest.mark.asyncio
async def test_generate_ppt_too_long_topic(mocker, client):
    """
    Test with a topic exceeding a reasonable length.
    If your backend has a length validation, this should ideally fail with 422.
    If it just passes it to OpenAI, it should still return 200 (mocked).
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"mocked ppt content")
    )
    
    long_topic = "a" * 1001 
    response = client.post("/generate-ppt/", json={"topic": long_topic})
    
    # IMPORTANT: Adjust this assertion based on your backend's actual validation.
    # If you have max_length in your Pydantic model (e.g., max_length=500), it should be 422.
    # If not, and it passes to OpenAI (which our mock handles), it's 200.
    # For now, assuming no explicit max_length validation leading to 422.
    assert response.status_code == 200 
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content"

@pytest.mark.asyncio
async def test_generate_ppt_empty_tone(client): # Removed mocker as this is a validation test
    """
    Test with an empty tone string.
    Expects a 422 Unprocessable Entity due to FastAPI validation (min_length=1 on tone).
    """
    # NO MOCKING HERE: This test specifically aims to hit FastAPI's Pydantic validation
    # which should return 422 before any external calls.
    response = client.post("/generate-ppt/", json={"topic": "Valid Topic", "tone": ""})
    
    assert response.status_code == 422
    assert "detail" in response.json()
    # Assert that the expected Pydantic error type is present for string_too_short
    assert any(err.get("type") == "string_too_short" for err in response.json()["detail"])


@pytest.mark.asyncio
async def test_generate_ppt_too_long_tone(mocker, client):
    """
    Test with a tone string exceeding a reasonable length.
    Similar to `test_generate_ppt_too_long_topic`, behavior depends on backend validation.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"mocked ppt content")
    )

    long_tone = "b" * 101 
    response = client.post("/generate-ppt/", json={"topic": "Valid Topic", "tone": long_tone})
    
    # IMPORTANT: Adjust this assertion based on your backend's actual validation.
    # If you have max_length in your Pydantic model, it should be 422.
    # If not, and it passes to OpenAI (which our mock handles), it's 200.
    assert response.status_code == 200 
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE
    assert response.content == b"mocked ppt content"

@pytest.mark.asyncio
async def test_generate_ppt_openai_api_failure(mocker, client):
    """
    Test case for when the OpenAI API call fails (e.g., network error, API key issue).
    Mocks `call_openai_with_retry` to raise an exception.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        side_effect=Exception("OpenAI API call failed during test") # Use a generic Exception for mocking
    )
    # create_presentation_from_slides_data won't be called if OpenAI fails, but good to keep it mocked
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"") # Dummy return
    )

    response = client.post("/generate-ppt/", json={"topic": "Any Topic"})
    
    # Assuming your FastAPI application handles this by returning a 500 error
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Failed to generate presentation content from AI" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_ppt_invalid_json_response_from_openai(mocker, client):
    """
    Test case for when OpenAI returns a non-JSON or malformed JSON response.
    The backend should ideally handle this gracefully.
    """
    mock_openai_response = get_mock_openai_success_response()
    mock_openai_response.choices[0].message.content = "This is not valid JSON" # Malformed content
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=mock_openai_response
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"") # Dummy return
    )

    response = client.post("/generate-ppt/", json={"topic": "Test JSON Error"})
    
    # Assuming your FastAPI application handles this by returning a 500 error
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Error parsing JSON from OpenAI response" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_ppt_empty_slides_from_openai(mocker, client):
    """
    Test case for when OpenAI returns valid JSON, but the 'slides' array is empty.
    The backend should ideally handle this gracefully.
    """
    mock_openai_response = get_mock_openai_success_response()
    mock_openai_response.choices[0].message.content = '{"slides": []}' # Empty slides
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=mock_openai_response
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        return_value=BytesIO(b"") # Dummy return
    )

    response = client.post("/generate-ppt/", json={"topic": "Test Empty Slides"})
    
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "OpenAI response did not contain valid slide data" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_ppt_create_presentation_failure(mocker, client):
    """
    Test case for when create_presentation_from_slides_data fails.
    """
    mocker.patch(
        "backend.main.call_openai_with_retry",
        return_value=get_mock_openai_success_response()
    )
    mocker.patch(
        "backend.main.create_presentation_from_slides_data",
        side_effect=Exception("Failed to create PPT file") # Mock the failure
    )

    response = client.post("/generate-ppt/", json={"topic": "Test PPT Creation Failure"})
    
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Failed to create presentation file" in response.json()["detail"]
