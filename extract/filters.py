import logging
class IgnoreThirdPartyCookieWarnings(logging.Filter):
    def filter(self, record):
        return 'Third-party cookie will be blocked. Learn more in the Issues tab.' not in record.getMessage()
    
class CustomHandler(logging.StreamHandler):
    def emit(self, record):
        if not self.filter(record):
            return
        super().emit(record)