import unittest
from app.services.chat_session import ChatSession
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse
from unittest.mock import ANY

from app.routers.chat import router
from app.models.chat import ChatResponse

class TestChat(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    def tearDown(self):
        pass

    @patch('app.routers.chat.session_manager')
    @patch('app.routers.chat.handle_regular_chat')
    def test_chat_endpoint_regular_with_existing_session(self, mock_handle_regular_chat, mock_session_manager):
        # Setup mock
        session_id = "test-session"
        mock_session = ChatSession()
        mock_session_manager.get_session.return_value = mock_session
        mock_response = ChatResponse(response="Test response")
        mock_handle_regular_chat.return_value = mock_response

        # Test request with existing session ID in header
        response = self.client.post(
            "/chat",
            json={"message": "Hello", "enable_streaming": False},
            headers={"X-Session-ID": session_id}
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Test response"})
        self.assertEqual(response.headers["X-Session-ID"], session_id)
        mock_session_manager.get_session.assert_called_with(session_id)

    @patch('app.routers.chat.session_manager')
    @patch('app.routers.chat.handle_regular_chat')
    def test_chat_endpoint_regular_new_session(self, mock_handle_regular_chat, mock_session_manager):
        # Setup mock for new session creation
        new_session_id = "new-session-id"
        mock_session_manager.create_session.return_value = new_session_id
        mock_response = ChatResponse(response="Test response")
        mock_handle_regular_chat.return_value = mock_response

        # Test request without session ID
        response = self.client.post(
            "/chat",
            json={"message": "Hello", "enable_streaming": False}
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Test response"})
        self.assertEqual(response.headers["X-Session-ID"], new_session_id)
        mock_session_manager.create_session.assert_called_once()

    @patch('app.routers.chat.session_manager')
    @patch('app.routers.chat.handle_streaming_chat')
    def test_chat_endpoint_streaming(self, mock_handle_streaming, mock_session_manager):
        # Setup mocks
        session_id = "test-session"
        mock_session = ChatSession()
        mock_session_manager.get_session.return_value = mock_session
        
        async def mock_stream():
            yield "Test streaming response"
        mock_streaming_response = StreamingResponse(
            mock_stream(), 
            headers={"X-Session-ID": session_id}
        )
        mock_handle_streaming.return_value = mock_streaming_response

        # Test request
        response = self.client.post(
            "/chat",
            json={"message": "Hello", "enable_streaming": True},
            headers={"X-Session-ID": session_id}
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_handle_streaming.assert_called_once_with(
            ANY,  # ChatRequest object
            session_id
        )

    @patch('app.routers.chat.session_manager')
    @patch('app.routers.chat.handle_regular_chat')  # Add this mock
    def test_chat_endpoint_invalid_session(self, mock_handle_regular_chat, mock_session_manager):
        # Setup mocks
        new_session_id = "new-session-id"
        mock_session_manager.get_session.side_effect = ValueError("Invalid session")
        mock_session_manager.create_session.return_value = new_session_id
        
        # Mock the response from handle_regular_chat
        mock_response = ChatResponse(response="Test response")
        mock_handle_regular_chat.return_value = mock_response

        # Test request with invalid session ID
        response = self.client.post(
            "/chat",
            json={"message": "Hello", "enable_streaming": False},
            headers={"X-Session-ID": "invalid-session"}
        )

        # Should create new session and continue
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Test response"})
        self.assertEqual(response.headers["X-Session-ID"], new_session_id)
        mock_session_manager.create_session.assert_called_once()
        # Verify handle_regular_chat was called with new session ID
        mock_handle_regular_chat.assert_called_once_with(ANY, new_session_id)

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
        mock_session.created_at = 1234567890  # Unix timestamp
        mock_session_manager.get_session.return_value = mock_session

        # Test request
        response = self.client.get("/chat/session/test-session")

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "session_id": "test-session",
            "message_count": 2,
            "created_at": 1234567890
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
