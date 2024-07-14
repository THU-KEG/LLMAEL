class UnsupportedLLMError(Exception): 
    def __init__(self, llms):
        self.message = f"UnsupportedLLMError: only {llms} augmentations are available for this EL model."
 
    def __str__(self):
        return self.message
    
    
class UnsupportedJoinStrategyError(Exception): 
    def __init__(self):
        self.message = "UnsupportedJoinStrategyError: only join-strategy IDs from 0 to 4 are available."
 
    def __str__(self):
        return self.message
    
class MentionNotFoundError(Exception): 
    def __init__(self, case_id):
        self.message = f"MentionNotFoundError: mention not found in original context at case_id {case_id}."
 
    def __str__(self):
        return self.message
    
class InconsistentMentionError(Exception): 
    def __init__(self, case_id):
        self.message = f"InconsistentMentionError: inconsistent mention found at case_id {case_id}."
 
    def __str__(self):
        return self.message