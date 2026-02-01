class AppException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ServiceUnexpectedError(AppException):
    """Exception raised for unexpected errors in services."""
    def __init__(self, detail: str = "An unexpected error occurred in the service."):
        self.message = detail
        self.status_code = 500
        super().__init__(self.message)

class TickerNotFoundException(AppException):
    """Exception raised when a ticker is not found in the database."""
    def __init__(self, ticker_code: str):
        self.ticker_code = ticker_code
        self.status_code = 404
        self.message = f"Ticker with code '{self.ticker_code}' not found."
        super().__init__(self.message)

class InvalidTimeframeException(AppException):
    """Exception raised for invalid timeframe inputs."""
    def __init__(self):
        self.message = f"Invalid timeframe."
        self.status_code = 422
        super().__init__(self.message)