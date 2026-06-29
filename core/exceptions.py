from fastapi import HTTPException, status

class VigilException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class UserNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

class InvalidCredentialsException(VigilException):
    def __init__(self):
        super().__init__(detail="Could not validate credentials", status_code=status.HTTP_401_UNAUTHORIZED)

class InactiveUserException(VigilException):
    def __init__(self):
        super().__init__(detail="Inactive user", status_code=status.HTTP_400_BAD_REQUEST)

class ForbiddenException(VigilException):
    def __init__(self, detail: str = "Operation forbidden"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

class UnauthorizedException(VigilException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class SessionNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Chat session not found", status_code=status.HTTP_404_NOT_FOUND)

class MessageNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Message not found", status_code=status.HTTP_404_NOT_FOUND)

class DocumentNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Document not found", status_code=status.HTTP_404_NOT_FOUND)

class TaskNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Task not found", status_code=status.HTTP_404_NOT_FOUND)

class NoteNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Note not found", status_code=status.HTTP_404_NOT_FOUND)

class GalleryImageNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Gallery image not found", status_code=status.HTTP_404_NOT_FOUND)

class ResearchProjectNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Research project not found", status_code=status.HTTP_404_NOT_FOUND)

class ProviderConfigNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Provider configuration not found", status_code=status.HTTP_404_NOT_FOUND)

class CalendarEventNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Calendar event not found", status_code=status.HTTP_404_NOT_FOUND)

class EmailAccountNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Email account not found", status_code=status.HTTP_404_NOT_FOUND)

class MemoryNotFoundException(VigilException):
    def __init__(self):
        super().__init__(detail="Memory not found", status_code=status.HTTP_404_NOT_FOUND)

class RateLimitExceededException(VigilException):
    def __init__(self):
        super().__init__(detail="Rate limit exceeded", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
