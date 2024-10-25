from abc import ABC, abstractmethod

class IFileService(ABC):
    @abstractmethod
    def save_file(self, file):
        pass

    @abstractmethod
    def is_csv_file(self, filename):
        pass