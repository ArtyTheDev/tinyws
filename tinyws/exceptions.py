class ConnectionClosed(Exception):
    """Raised when a connection is closed or disconnected."""

    def __init__(self, message: str, code: int = 1000) -> None:
        self.code = code
        
        super().__init__(message)