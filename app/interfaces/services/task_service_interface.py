from abc import ABC, abstractmethod

class ITaskService(ABC):
    @abstractmethod
    def create_task(self, task_id, filename, file_path):
        pass

    @abstractmethod
    def update_task(self, task_id, update_fields = {}, update_query = {}):
        pass
