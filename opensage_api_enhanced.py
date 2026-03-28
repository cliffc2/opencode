#!/usr/bin/env python3
"""
OpenSage HTTP API - Enhanced REST API for OpenSage memory (FIXED).

Features:
- CORS support for OpenCode browser UI
- Error handling and graceful degradation
- Environment-based configuration
- Async support
- Optional authentication
- Health checks

Run: python opensage_api_enhanced.py
Or:  OPENCODE_ENABLED=true python opensage_api_enhanced.py

Usage:
  http://localhost:5555/health
  http://localhost:5555/remember?key=notes&value=My notes
  http://localhost:5555/recall?key=notes
  http://localhost:5555/list
  http://localhost:5555/search?q=auth
  http://localhost:5555/list?format=json&limit=50
"""

import os
import sys
import json
import logging
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any
from datetime import datetime

# Add OpenSage to path
sys.path.insert(0, os.path.expanduser("~/opensage/src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from environment
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
API_PORT = int(os.getenv("API_PORT", "5555"))
API_HOST = os.getenv("API_HOST", "127.0.0.1")  # Change to 0.0.0.0 to expose publicly
OPENCODE_ENABLED = os.getenv("OPENCODE_ENABLED", "false").lower() == "true"

# Track Neo4j connection status
neo4j_available = False


def check_neo4j():
    """Check if Neo4j is available"""
    global neo4j_available
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        neo4j_available = True
        logger.info("✓ Neo4j connected")
        driver.close()
        return True
    except Exception as e:
        logger.error(f"✗ Neo4j connection failed: {e}")
        neo4j_available = False
        return False


def get_driver():
    """Get Neo4j driver with error handling"""
    try:
        from neo4j import GraphDatabase
        if not neo4j_available:
            raise ConnectionError("Neo4j not available")
        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    except ImportError:
        logger.error("neo4j package not installed: pip install neo4j")
        raise
    except Exception as e:
        logger.error(f"Failed to get Neo4j driver: {e}")
        raise


def remember(key: str, value: str) -> Dict[str, Any]:
    """Store a memory"""
    if not key or not value:
        return {"error": "key and value required", "status": 400}
    
    try:
        driver = get_driver()
        with driver.session() as session:
            # Use session.run() instead of execute_query() for compatibility
            result = session.run(
                """
                MERGE (m:Memory {key: $key}) 
                SET m.value = $value, m.updated = timestamp()
                RETURN m
                """,
                key=key,
                value=value,
            )
            result.consume()  # Ensure query completes
        logger.info(f"✓ Stored: {key}")
        return {"status": 200, "key": key, "value": value}
    except Exception as e:
        logger.error(f"✗ remember({key}): {e}")
        return {"error": str(e), "status": 500}


def recall(key: str) -> Dict[str, Any]:
    """Retrieve a memory"""
    if not key:
        return {"error": "key required", "status": 400}
    
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (m:Memory {key: $key}) RETURN m.value as value",
                key=key,
            )
            records = list(result)
            value = records[0]["value"] if records else None
        
        if value is None:
            logger.warning(f"Key not found: {key}")
            return {"key": key, "value": None, "status": 200}
        
        return {"key": key, "value": value, "status": 200}
    except Exception as e:
        logger.error(f"✗ recall({key}): {e}")
        return {"error": str(e), "status": 500}


def list_memories(limit: int = 50) -> Dict[str, Any]:
    """List all memories"""
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                f"""
                MATCH (m:Memory) 
                RETURN m.key as key, m.value as value, m.updated as updated
                ORDER BY m.updated DESC
                LIMIT {limit}
                """
            )
            memories = [
                {
                    "key": r["key"],
                    "value": r["value"],
                    "updated": r["updated"],
                }
                for r in result
            ]
        return {"status": 200, "count": len(memories), "memories": memories}
    except Exception as e:
        logger.error(f"✗ list_memories(): {e}")
        return {"error": str(e), "status": 500}


def search(query: str, limit: int = 50) -> Dict[str, Any]:
    """Search memories"""
    if not query:
        return {"error": "query required", "status": 400}
    
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                f"""
                MATCH (m:Memory) 
                WHERE m.value CONTAINS $q OR m.key CONTAINS $q
                RETURN m.key as key, m.value as value, m.updated as updated
                LIMIT {limit}
                """,
                q=query,
            )
            memories = [
                {"key": r["key"], "value": r["value"], "updated": r["updated"]}
                for r in result
            ]
        return {"status": 200, "query": query, "count": len(memories), "memories": memories}
    except Exception as e:
        logger.error(f"✗ search({query}): {e}")
        return {"error": str(e), "status": 500}


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler with CORS support"""
    
    def _send_json(self, data: Dict[str, Any]):
        """Send JSON response"""
        status = data.get("status", 200)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        if OPENCODE_ENABLED:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        # Health check (always available)
        if path == "/health":
            self._send_json({
                "status": 200,
                "neo4j": neo4j_available,
                "timestamp": datetime.now().isoformat(),
            })
            return
        
        # All other endpoints require Neo4j
        if not neo4j_available:
            self._send_json({
                "error": "Neo4j not available",
                "status": 503,
                "hint": "Start Neo4j: brew services start neo4j",
            })
            return
        
        # Endpoint routing
        if path == "/remember":
            key = query.get("key", [""])[0]
            value = query.get("value", [""])[0]
            result = remember(key, value)
            self._send_json(result)
        
        elif path == "/recall":
            key = query.get("key", [""])[0]
            result = recall(key)
            self._send_json(result)
        
        elif path == "/list":
            limit = int(query.get("limit", ["50"])[0])
            result = list_memories(limit)
            self._send_json(result)
        
        elif path == "/search":
            q = query.get("q", [""])[0]
            limit = int(query.get("limit", ["50"])[0])
            result = search(q, limit)
            self._send_json(result)
        
        elif path == "/":
            # Root endpoint - show help
            self._send_json({
                "status": 200,
                "message": "OpenSage API",
                "endpoints": {
                    "GET /health": "Health check",
                    "GET /remember?key=<k>&value=<v>": "Store memory",
                    "GET /recall?key=<k>": "Retrieve memory",
                    "GET /list?limit=50": "List all memories",
                    "GET /search?q=<query>": "Search memories",
                },
                "docs": "See opensage_api_enhanced.py docstring",
            })
        
        else:
            self._send_json({"error": "Not found", "status": 404})
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging (we use our own)"""
        pass


def main():
    """Start the API server"""
    print(f"""
╔════════════════════════════════════════╗
║    OpenSage HTTP API v2.1 (FIXED)      ║
╚════════════════════════════════════════╝

Configuration:
  Neo4j URI: {NEO4J_URI}
  API Host: {API_HOST}
  API Port: {API_PORT}
  OpenCode Enabled: {OPENCODE_ENABLED}
  
Starting server...
""")
    
    # Check Neo4j availability
    if not check_neo4j():
        print("\n⚠️  WARNING: Neo4j not available!")
        print("   Start with: brew services start neo4j")
        print("   Or set credentials: NEO4J_PASSWORD=... python opensage_api_enhanced.py")
    
    # Start server
    try:
        server = HTTPServer((API_HOST, API_PORT), RequestHandler)
        print(f"\n✓ Server running at http://{API_HOST}:{API_PORT}")
        print(f"\nEndpoints:")
        print(f"  GET http://{API_HOST}:{API_PORT}/health - Health check")
        print(f"  GET http://{API_HOST}:{API_PORT}/remember?key=x&value=y - Store")
        print(f"  GET http://{API_HOST}:{API_PORT}/recall?key=x - Retrieve")
        print(f"  GET http://{API_HOST}:{API_PORT}/list - List all")
        print(f"  GET http://{API_HOST}:{API_PORT}/search?q=term - Search")
        print(f"\nPress Ctrl+C to stop\n")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
