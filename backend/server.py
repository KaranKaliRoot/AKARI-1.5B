"""AKARI Backend HTTP API Server.

Standard library http.server implementation providing local API endpoints for AKARI:
- GET  /api/health
- POST /api/chat
- GET  /api/conversations
- GET  /api/conversations/{id}
- DELETE /api/conversations/{id}
"""

import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from backend import config
    from backend.conversation import ConversationManager
    from backend.database import AkariDB
except ImportError:
    import config
    from conversation import ConversationManager
    from database import AkariDB

manager = ConversationManager()
db = AkariDB()


class AkariHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AKARI backend."""

    def log_message(self, format, *args):
        """Standard log output to stdout/stderr."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def _send_json(self, data: dict, status: int = 200):
        """Utility to send JSON responses."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message: str, status: int = 400):
        self._send_json({"error": message, "status": status}, status=status)

    def do_OPTIONS(self):
        """CORS preflight handling."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # Use full path including leading slash for matching
        path = self.path.split("?")[0]
        if path.endswith("/") and len(path) > 1:
            path = path.rstrip("/")

        if path == "/api/health":
            self.handle_health()
        elif path == "/api/conversations":
            self.handle_list_conversations()
        elif path.startswith("/api/conversations/"):
            session_id = path[len("/api/conversations/"):]
            self.handle_get_conversation(session_id)
        elif path in ("", "/", "/index.html"):
            self.serve_static("frontend/index.html", "text/html; charset=utf-8")
        elif path.startswith("/static/"):
            sub_path = path[len("/static/"):]
            self.serve_static(f"frontend/static/{sub_path}")
        else:
            self._send_error(f"Not Found: {path}", 404)

    def serve_static(self, rel_path: str, default_content_type: str = None):
        """Serve static frontend files."""
        file_path = ROOT_DIR / rel_path
        if not file_path.exists() or not file_path.is_file():
            self._send_error("Not Found", 404)
            return
        if default_content_type:
            content_type = default_content_type
        elif file_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif file_path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif file_path.suffix in (".html", ".htm"):
            content_type = "text/html; charset=utf-8"
        elif file_path.suffix == ".png":
            content_type = "image/png"
        elif file_path.suffix in (".jpg", ".jpeg"):
            content_type = "image/jpeg"
        else:
            content_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self._send_error(str(e), 500)

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")

        if path == "/api/chat":
            self.handle_chat()
        else:
            self._send_error("Not Found", 404)

    def do_DELETE(self):
        path = self.path.split("?")[0].rstrip("/")

        if path.startswith("/api/conversations/"):
            session_id = path[len("/api/conversations/"):]
            self.handle_delete_conversation(session_id)
        else:
            self._send_error("Not Found", 404)

    def handle_health(self):
        """GET /api/health - check backend and llama-server status."""
        llama_healthy = False
        try:
            req = urllib.request.Request(f"http://{config.LLAMA_HOST}:{config.LLAMA_PORT}/health")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    llama_healthy = True
        except Exception:
            llama_healthy = False

        self._send_json({
            "status": "ok",
            "project": "AKARI",
            "llama_server": "healthy" if llama_healthy else "unavailable",
            "active_sessions": len(manager.list_sessions())
        })

    def handle_list_conversations(self):
        """GET /api/conversations - list all sessions."""
        sessions = manager.list_sessions()
        self._send_json({"conversations": sessions})

    def handle_get_conversation(self, session_id: str):
        """GET /api/conversations/{id} - fetch full message history for a session."""
        session = manager.get_session(session_id)
        if not session:
            self._send_error(f"Session {session_id} not found", 404)
            return

        self._send_json({
            "session_id": session.session_id,
            "mode": session.mode,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": session.messages
        })

    def handle_delete_conversation(self, session_id: str):
        """DELETE /api/conversations/{id} - delete a session."""
        success = manager.delete_session(session_id)
        if not success:
            self._send_error(f"Session {session_id} not found", 404)
            return

        self._send_json({"message": f"Session {session_id} deleted", "success": True})

    def handle_chat(self):
        """POST /api/chat - process chat message with llama-server backend."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_error("Empty request body", 400)
            return

        try:
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            self._send_error(f"Invalid JSON payload: {str(e)}", 400)
            return

        user_message = payload.get("message")
        if not user_message or not isinstance(user_message, str):
            self._send_error("Missing or invalid 'message' field", 400)
            return

        session_id = payload.get("session_id")
        mode = payload.get("mode", "default")
        temperature = payload.get("temperature", config.DEFAULT_TEMPERATURE)
        max_tokens = payload.get("max_tokens", config.DEFAULT_MAX_TOKENS)

        # Get or create conversation session
        session = manager.get_or_create(session_id=session_id, mode=mode)

        # Add user message
        session.add_user_message(user_message)

        # RAG Implementation: Search knowledge base
        knowledge_context = ""
        hits = db.search_all_domains(user_message)
        if hits:
            knowledge_context += "Relevant Knowledge Found:\n"
            for h in hits[:5]:
                knowledge_context += f"- [{h['domain']}] {h['key']}: {h['details']}\n"
        else:
            # Fallback handling & logging for zero-hit retrieval queries
            unbacked_log = ROOT_DIR / "data" / "unbacked_queries.json"
            try:
                unbacked_data = []
                if unbacked_log.exists():
                    with open(unbacked_log, "r", encoding="utf-8") as f:
                        unbacked_data = json.load(f)
                unbacked_data.append({"query": user_message, "timestamp": str(session.updated_at)})
                with open(unbacked_log, "w", encoding="utf-8") as f:
                    json.dump(unbacked_data, f, ensure_ascii=False, indent=2)
            except Exception as log_err:
                sys.stderr.write(f"Failed to log unbacked query: {log_err}\n")

            knowledge_context = (
                "No verified local database entries matched the query.\n"
                "INSTRUCTION: Answer using general background knowledge. You MUST include this notice to the user:\n"
                '\"Note: This explanation is based on general background knowledge rather than a verified local database record.\"\n'
            )

        # Build prompt payload for llama-server
        llm_messages = session.get_messages_for_llm()

        # Update system prompt with knowledge context if found
        from backend.persona import build_system_prompt
        updated_sys = build_system_prompt(mode=mode, knowledge=knowledge_context)
        llm_messages[0]["content"] = updated_sys

        llama_payload = {
            "model": "models/akari.gguf",
            "messages": llm_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Forward request to llama-server
        req_body = json.dumps(llama_payload).encode("utf-8")
        req = urllib.request.Request(
            config.LLAMA_URL,
            data=req_body,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=config.REQUEST_TIMEOUT_SECONDS) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

                # Extract response text
                choices = resp_data.get("choices", [])
                if not choices:
                    self._send_error("Empty response from inference engine", 500)
                    return

                assistant_text = choices[0].get("message", {}).get("content", "")

                # Save assistant response to session history
                session.add_assistant_message(assistant_text)

                self._send_json({
                    "session_id": session.session_id,
                    "response": assistant_text,
                    "mode": session.mode,
                    "usage": resp_data.get("usage", {})
                })

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            self._send_error(f"llama-server HTTP Error {e.code}: {err_body}", 502)
        except urllib.error.URLError as e:
            self._send_error(f"llama-server unavailable: {e.reason}", 503)
        except Exception as e:
            self._send_error(f"Internal server error: {str(e)}", 500)


def run_server(host: str = None, port: int = None):
    host = host or config.BACKEND_HOST
    port = port or config.BACKEND_PORT
    server_address = (host, port)
    httpd = HTTPServer(server_address, AkariHTTPRequestHandler)
    print(f"AKARI Backend running at http://{host}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()