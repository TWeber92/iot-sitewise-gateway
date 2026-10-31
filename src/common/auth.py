import base64
import os
from src.common.logger import Logger


class Auth:
    @staticmethod
    def check_basic_auth(headers):
        """
        Validates the Authorization header against environment variables.
        Returns True if valid, False otherwise.
        """
        auth_header = headers.get("authorization") or headers.get("Authorization")

        if not auth_header:
            return False

        try:
            scheme, encoded = auth_header.split(" ")
            if scheme.lower() != "basic":
                return False

            decoded = base64.b64decode(encoded).decode("utf-8")
            username, password = decoded.split(":")

            # Compare against Environment Variables
            expected_user = os.environ.get("BASIC_ADMIN")
            expected_pass = os.environ.get("BASIC_PASS")

            if username == expected_user and password == expected_pass:
                return True

            Logger.emit(
                "warn",
                {
                    "source": "Auth",
                    "message": f"Failed login attempt for user: {username}",
                },
            )
            return False

        except Exception as e:
            Logger.emit(
                "error", {"source": "Auth", "message": f"Auth parsing error: {str(e)}"}
            )
            return False
