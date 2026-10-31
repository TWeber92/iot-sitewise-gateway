import json
from datetime import datetime, timezone
from collections import defaultdict


class Logger:
    # Static registry holding the subscribers
    _listeners = defaultdict(list)

    @classmethod
    def on(cls, event_name: str, callback):
        """Subscribe a function to an event."""
        cls._listeners[event_name].append(callback)

    @classmethod
    def emit(cls, event_name: str, data):
        """Publish an event to all subscribers."""
        if event_name not in cls._listeners:
            return

        for callback in cls._listeners[event_name]:
            callback(data)

    # ---------------------------------------------------
    # Built-in Subscribers (registered when the app starts)
    # ---------------------------------------------------
    @classmethod
    def setup_default_logger(cls):
        """Call this in Main to register the default console logging."""

        # Subscribe to the 'error' event
        cls.on("error", cls._print_error)

        # Subscribe to the 'info' event
        cls.on("info", cls._print_info)

    @staticmethod
    def _print_error(data):
        """Formats and prints errors to the console."""
        timestamp = datetime.now(timezone.utc).isoformat()
        source = data.get("source", "Unknown")
        message = data.get("message", str(data))
        context = data.get("context", {})

        log_entry = {
            "timestamp": timestamp,
            "level": "ERROR",
            "source": source,
            "message": message,
            "context": context,
        }
        # Print as a JSON string so it's easy to read in Render logs
        print(f"🔴 {json.dumps(log_entry)}")

    @staticmethod
    def _print_info(data):
        timestamp = datetime.now(timezone.utc).isoformat()
        source = data.get("source", "Unknown")
        message = data.get("message", str(data))
        print(f"🔵 [{timestamp}] [{source}] {message}")
