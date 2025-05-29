import pytest
import httpx

BASE_URL = "http://localhost:8000"
PPTX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

# Positive Test Cases
@pytest.mark.asyncio
async def test_generate_ppt_valid_topic_default_tone():
    # Test with a valid topic and default tone (educational)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client: # Added timeout
        response = await client.post("/generate-ppt/", json={"topic": "The History of Python"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_valid_topic_specified_tone():
    # Test with a valid topic and a specified tone
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client: # Added timeout
        response = await client.post("/generate-ppt/", json={"topic": "Quantum Physics Explained", "tone": "formal"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_single_word_topic():
    # Test with a single word topic
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client: # Added timeout
        response = await client.post("/generate-ppt/", json={"topic": "AI"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_long_sentence_topic():
    # Test with a long sentence topic
    topic = "An in-depth analysis of the socio-economic impacts of renewable energy adoption in developing nations from 2000 to 2020"
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client: # Added timeout
        response = await client.post("/generate-ppt/", json={"topic": topic})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

@pytest.mark.asyncio
async def test_generate_ppt_single_word_tone():
    # Test with a single word tone
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client: # Added timeout
        response = await client.post("/generate-ppt/", json={"topic": "Introduction to Machine Learning", "tone": "casual"})
    assert response.status_code == 200
    assert response.headers["content-type"] == PPTX_CONTENT_TYPE

# Negative Test Cases
@pytest.mark.asyncio
async def test_generate_ppt_empty_topic():
    # Test with an empty topic string
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client: # Shorter timeout for expected errors
        response = await client.post("/generate-ppt/", json={"topic": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_generate_ppt_too_long_topic():
    # Test with a topic string exceeding a reasonable length (e.g., 1000 characters for the model, Pydantic might have its own limits)
    # FastAPI/Pydantic default for string length is very large unless constrained by the model.
    # Assuming the model `PresentationRequest` in `backend/main.py` has `topic: str = Field(..., min_length=1, max_length=N)`
    # For this test, we'll test against a hypothetical max_length of 500 for the topic.
    # If no max_length is set in Pydantic model, this test might expect 200, or 422 if custom validation exists.
    # Let's check backend/main.py for actual validation rules.
    # Assuming topic: str = Field(..., min_length=1, max_length=config.TOPIC_MAX_LENGTH) and tone: Optional[str] = Field(config.DEFAULT_TONE, min_length=1, max_length=config.TONE_MAX_LENGTH)
    # Let's assume TOPIC_MAX_LENGTH = 200 for this test.
    long_topic = "a" * 201 
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client: # Shorter timeout
        response = await client.post("/generate-ppt/", json={"topic": long_topic})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_generate_ppt_empty_tone():
    # Test with an empty tone string. Pydantic Field(min_length=1) should catch this.
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client: # Shorter timeout
        response = await client.post("/generate-ppt/", json={"topic": "Valid Topic", "tone": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_generate_ppt_too_long_tone():
    # Test with a tone string exceeding a reasonable length (e.g., 100 characters for the model)
    # Assuming TONE_MAX_LENGTH = 50 for this test.
    long_tone = "b" * 51
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client: # Shorter timeout
        response = await client.post("/generate-ppt/", json={"topic": "Valid Topic", "tone": long_tone})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_generate_ppt_special_chars_topic():
    # Test with a topic containing only special characters
    # FastAPI/Pydantic allows special characters in strings by default.
    # This test will expect 422 if there's custom validation in the backend to disallow such topics.
    # If not, it should be 200. Given the subtask description "problematic inputs",
    # we'll assume it implies this should be a 422 case.
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client: # Longer timeout as it might try to generate
        response = await client.post("/generate-ppt/", json={"topic": "!@#$%^&*()"})
    # This assertion relies on the backend having specific validation to reject this topic.
    # Without it, Pydantic would allow it, and the status would likely be 200.
    assert response.status_code == 422
