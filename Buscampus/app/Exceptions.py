class ServiceExecutionFailure(Exception):
    def __init__(self, public_message: str, internal_detail: str) -> None:
        self.public_message = public_message
        self.internal_detail = internal_detail
        super().__init_(internal_detail)
        
        
    
class NoAvailableGeminiKeyError(ServiceExecutionFailure):
    pass

class SmsParsingError(ServiceExecutionFailure):
    pass
    
class WalletOperationFailure(ServiceExecutionFailure):
    pass
    
        
class PaymentIntegrityError(ServiceExecutionFailure):
    pass
    
 
 
