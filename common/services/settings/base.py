from abc import ABC, abstractmethod

from common.schemas.bitads import FormulaParams


class SettingsContainer(ABC):
    """Abstract base class for a Settings Container.

    This class defines the interface for a container that holds settings parameters.
    Subclasses must implement the getter and setter for the settings property.

    Properties:
        settings (FormulaParams): Gets or sets the settings parameters.
    """

    @property
    @abstractmethod
    def settings(self) -> FormulaParams:
        """Gets the settings parameters.

        Returns:
            FormulaParams: The current settings parameters.
        """
        pass

    @settings.setter
    @abstractmethod
    def settings(self, params: FormulaParams) -> None:
        """Sets the settings parameters.

        Args:
            params (FormulaParams): The new settings parameters.
        """
        pass
