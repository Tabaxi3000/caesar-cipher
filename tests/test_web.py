"""
test_web.py

Tests for the Flask web visualizer endpoints

Skips entirely when Flask (the optional web extra) is not installed.

Tests:
  index page renders and references Chart.js
  /analyze returns a 26-length frequency array and letter count
  /analyze handles empty input without dividing by zero
  /crack returns 26 ranked candidates and finds the plaintext
  /crack handles empty input, reporting infinite scores as null

Connects to:
  web.py - the Flask app under test
  cipher.py - used to build ciphertext for the crack endpoint
"""

import pytest

pytest.importorskip("flask")

from caesar_cipher.cipher import CaesarCipher
from caesar_cipher.web import create_app


@pytest.fixture
def client():  # type: ignore[no-untyped-def]
    """
    Provide a Flask test client for the visualizer app
    """
    return create_app().test_client()


class TestIndex:
    def test_index_renders(self, client) -> None:  # type: ignore[no-untyped-def]
        """
        Confirms the index page loads and pulls in Chart.js
        """
        response = client.get("/")
        assert response.status_code == 200
        assert b"chart.js" in response.data


class TestAnalyzeEndpoint:
    def test_returns_frequencies(self, client) -> None:  # type: ignore[no-untyped-def]
        """
        Confirms /analyze returns 26 frequency values and the letter count
        """
        response = client.post("/analyze", json = {"text": "HELLO WORLD"})
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["frequencies"]) == 26
        assert len(data["labels"]) == 26
        assert data["count"] == 10

    def test_empty_input(self, client) -> None:  # type: ignore[no-untyped-def]
        """
        Confirms /analyze handles empty text with zeroed frequencies
        """
        response = client.post("/analyze", json = {"text": ""})
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0
        assert set(data["frequencies"]) == {0.0}


class TestCrackEndpoint:
    def test_returns_ranked_candidates(self, client) -> None:  # type: ignore[no-untyped-def]
        """
        Confirms /crack returns all 26 candidates and recovers the plaintext
        """
        ciphertext = CaesarCipher(key = 3).encrypt(
            "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        )
        response = client.post("/crack", json = {"text": ciphertext})
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["candidates"]) == 26
        texts = [candidate["text"] for candidate in data["candidates"]]
        assert "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG" in texts

    def test_empty_input_scores_null(self, client) -> None:  # type: ignore[no-untyped-def]
        """
        Confirms empty input yields candidates with null (infinite) scores
        """
        response = client.post("/crack", json = {"text": ""})
        assert response.status_code == 200
        data = response.get_json()
        assert data["candidates"][0]["score"] is None
