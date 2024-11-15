import unittest
from app.services.chat_session import ChatSession
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse
from unittest.mock import ANY

from app.routers.chat import router
from app.models.chat import ChatRequest, ChatResponse

class TestChat(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    def tearDown(self):
        pass

    @patch('app.routers.chat.session_manager')
    @patch('app.routers.chat.handle_regular_chat')
    def test_chat_endpoint_regular(self, mock_handle_regular_chat, mock_session_manager):
        # Setup mock
        mock_session = ChatSession()
        mock_session_manager.get_session.return_value = mock_session
        mock_response = ChatResponse(response="Test response", session_id="test-session")
        mock_handle_regular_chat.return_value = mock_response

        # Test request
        response = self.client.post(
            "/chat",
            json={
                "message": "Hello",
                "session_id": "test-session",
                "enable_streaming": False
            }
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "response": "Test response",
            "session_id": "test-session"
        })

    @patch('app.routers.chat.session_manager')
    @patch('app.routers.chat.handle_streaming_chat')
    def test_chat_endpoint_streaming(self, mock_handle_streaming, mock_session_manager):

        mock_session = ChatSession()
        mock_session_manager.get_session.return_value = mock_session
        
        # Setup mock
        async def mock_stream():
            yield "Test streaming response"
            
        mock_streaming_response = StreamingResponse(mock_stream())
        mock_handle_streaming.return_value = mock_streaming_response

        # Test request
        response = self.client.post(
            "/chat",
            json={
                "message": "Hello",
                "session_id": "85378f61-0b3e-4bc6-a82c-d9d1c3d0f6f4",
                "enable_streaming": True
            }
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_handle_streaming.assert_called_once_with(
            ANY,  # ChatRequest object
            "85378f61-0b3e-4bc6-a82c-d9d1c3d0f6f4"  # session_id
        )

    def test_chat_endpoint_error(self):
        # Test request with invalid data
        response = self.client.post(
            "/chat",
            json={}  # Invalid request body
        )

        # Assertions
        self.assertEqual(response.status_code, 422)  # Validation error

    @patch('app.routers.chat.session_manager')
    def test_get_session_status(self, mock_session_manager):
        # Setup mock
        mock_session = MagicMock()
        mock_session.messages = ["message1", "message2"]
        mock_session.created_at = "2024-01-01T00:00:00"
        mock_session_manager.get_session.return_value = mock_session

        # Test request
        response = self.client.get("/chat/session/test-session")

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "session_id": "test-session",
            "message_count": 2,
            "created_at": "2024-01-01T00:00:00"
        })

    @patch('app.routers.chat.session_manager')
    def test_get_session_status_not_found(self, mock_session_manager):
        # Setup mock to raise ValueError
        mock_session_manager.get_session.side_effect = ValueError("Session not found")

        # Test request
        response = self.client.get("/chat/session/nonexistent-session")

        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Session not found"})
