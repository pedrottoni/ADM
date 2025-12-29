from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    @abstractmethod
    def run(self, *args, **kwargs):
        pass
        
    def log(self, message: str):
        print(f"[{self.agent_name}]: {message}")
