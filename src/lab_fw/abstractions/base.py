from abc import ABC, abstractmethod

class BasePage(ABC):

    @abstractmethod
    def open(self):
        ...

    @property
    @abstractmethod
    def path(self):
        ...

