from common.schemas.bitads import FormulaParams
from common.services.settings.base import SettingsContainer


class SettingsContainerImpl(SettingsContainer):
    """Implementation of the SettingsContainer abstract base class.

    This class provides a concrete implementation of the SettingsContainer
    interface, managing settings parameters.

    Attributes:
        _params (FormulaParams): The current settings parameters.
    """

    def __init__(
        self, params: FormulaParams = FormulaParams.default_instance()
    ):
        """Initializes the SettingsContainerImpl with the given parameters.

        Args:
            params (FormulaParams, optional): The initial settings parameters.
            Defaults to a default instance of FormulaParams.
        """
        self._params = params

    @property
    def settings(self) -> FormulaParams:
        """Gets the current settings parameters.

        Returns:
            FormulaParams: The current settings parameters.
        """
        return self._params

    @settings.setter
    def settings(self, params: FormulaParams) -> None:
        """Sets the settings parameters.

        Args:
            params (FormulaParams): The new settings parameters.
        """
        self._params = params
