class AuthError(Exception):
    
    def __init__(self, public_message: str, internal_detail: str) -> None:
        
        self.public_message = public_message
        self.internal_detail = internal_detail or public_message
        super().__init__(internal_detail)
        