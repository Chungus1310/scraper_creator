from utils import handle_error

class TargetParser:
    def __init__(self):
        self.target_description = None

    def set_target_description(self, description):
        """Sets the target description."""
        self.target_description = description

    def get_target_description(self):
        """Gets the target description."""
        if not self.target_description:
            handle_error("Target description not set.")
            return None
        return self.target_description