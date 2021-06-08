import sys
import logging
# class logging2(logging.getLogger("type")):
# 
#     def error2(self, msg):
#         self.error(msg)
#         if self.level < logging.INFO:
#             raise Exception

class LWOLogger:
    def __new__(self, type, loglevel=logging.INFO):
        self.l = logging.getLogger(type)
        self.l.setLevel(loglevel)
        
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(loglevel)
        formatter = logging.Formatter('%(levelname)7s: %(name)5s - %(message)s')
        stdout_handler.setFormatter(formatter)
        
        handler_present = False
        for handler in self.l.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler_present = True
        
        if not handler_present:
            self.l.addHandler(stdout_handler)
        return self.l
