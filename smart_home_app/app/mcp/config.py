import os

MCP_CONFIG = {
    "refrigerator": {
        "url": os.environ.get("REFRIGERATOR_MCP_URL", "http://localhost:8001/sse"),
        "transport": "sse",
    },
    "induction": {
        "url": os.environ.get("INDUCTION_MCP_URL", "http://localhost:8002/sse"),
        "transport": "sse",
    },
    "microwave": {
        "url": os.environ.get("MICROWAVE_MCP_URL", "http://localhost:8003/sse"),
        "transport": "sse",
    },
    "mobile": {
        "url": os.environ.get("MOBILE_MCP_URL", "http://localhost:8004/sse"),
        "transport": "sse",
    },
    "cooking": {
        "url": os.environ.get("COOKING_MCP_URL", "http://localhost:8005/sse"),
        "transport": "sse",
    },
}
