import json
import os
from typing import Union, Optional

import bittensor as bt

from common.helpers import const
from common.helpers.logging import (
    LogLevel,
    magenta,
    colorize,
    Color,
    yellow,
    red,
)
from common.schemas.bitads import GetMinerUniqueIdResponse, Campaign
from common.services.storage.base import BaseStorage
from template.base.validator import BaseValidatorNeuron


class FileStorage(BaseStorage):
    """File-based storage implementation of the BaseStorage abstract class.

    This class provides methods to save and retrieve campaign and unique URL
    information to and from the file system.

    Attributes:
        _root_dir (str): The root directory for storage.
        _hotkey (str): The hotkey identifier.
        _neuron_type (str): The type of the neuron.
    """

    def __init__(
        self, neuron_type: str, hotkey: str, root_dir: str = const.ROOT_DIR
    ):
        """Initializes the FileStorage with the given parameters and creates necessary directories.

        Args:
            neuron_type (str): The type of the neuron.
            hotkey (str): The hotkey identifier.
            root_dir (str, optional): The root directory for storage. Defaults to const.ROOT_DIR.
        """
        self._root_dir = root_dir
        self._hotkey = hotkey
        self._neuron_type = neuron_type
        self._create_dirs()

    def _create_dirs(self):
        """Creates the necessary directories for storage."""
        directories = [
            self._root_dir,
            f"{self._root_dir}/{self._neuron_type}",
            f"{self._root_dir}/{self._neuron_type}/{self._hotkey}",
            f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/campaign_id",
            f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link",
        ]

        if self._neuron_type == BaseValidatorNeuron.neuron_type:
            directories.extend(
                [
                    f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link_score",
                    f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link_stats",
                ]
            )

        for path in directories:
            if not os.path.exists(path):
                os.makedirs(path)
                bt.logging.info(
                    prefix=LogLevel.LOCAL,
                    msg=magenta(f"Created directory: {path}"),
                )

    def save_campaign(self, task: Campaign):
        """Saves a campaign to the file system.

        Args:
            task (Campaign): The campaign to save.
        """
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/campaign_id/{task.product_unique_id}.json"
        with open(path, "w") as file:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=yellow(f"Save campaign to: {path}"),
            )
            file.write(task.model_dump_json(indent=4, by_alias=True))

    def remove_campaign(self, campaign_id: Union[int, str]):
        """Removes a campaign from the file system by its ID.

        Args:
            campaign_id (Union[int, str]): The ID of the campaign to remove.
        """
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/campaign_id/{campaign_id}_{self._hotkey}.json"
        if os.path.exists(path):
            os.remove(path)
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=colorize(Color.YELLOW, f"Remove campaign file: {path}"),
            )

    def save_miner_unique_url(
        self, product_unique_id: str, data: GetMinerUniqueIdResponse
    ):
        """Saves a miner's unique URL information to the file system.

        Args:
            product_unique_id (str): The unique ID of the product.
            data (GetMinerUniqueIdResponse): The data associated with the miner's unique URL.
        """
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link/{product_unique_id}_{self._hotkey}.json"
        with open(path, "w") as file:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=yellow(f"Save campaign unique url to: {path}"),
            )
            file.write(data.model_dump_json(indent=4, by_alias=True))

    # def save_miner_unique_url_stats(self, data: Aggregation):
    #     path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link_stats/{data.product_unique_id}_{data.product_item_unique_id}.json"
    #     with open(path, "w") as file:
    #         bt.logging.info(
    #             prefix=LogLevel.LOCAL,
    #             msg=yellow(
    #                 f"Save campaign unique url statistics to: {path}",
    #             ),
    #         )
    #         file.write(data.model_dump_json(indent=4, by_alias=True))
    #
    # def save_miner_unique_url_score(
    #     self,
    #     product_unique_id: Union[int, str],
    #     product_item_unique_id: Union[int, str],
    #     data: Score,
    # ):
    #     path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link_score/{product_unique_id}_{product_item_unique_id}.json"
    #     with open(path, "w") as file:
    #         bt.logging.info(
    #             prefix=LogLevel.LOCAL,
    #             msg=yellow(
    #                 f"Save campaign unique url score to: {path}",
    #             ),
    #         )
    #         file.write(data.model_dump_json(indent=4, by_alias=True))
    def unique_link_exists(self, campaign_id: str) -> bool:
        """Checks if a unique link exists for a given campaign ID.

        Args:
            campaign_id (str): The ID of the campaign.

        Returns:
            bool: True if the unique link exists, False otherwise.
        """
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link/{campaign_id}_{self._hotkey}.json"
        return os.path.exists(path)

    def get_unique_url(
        self, campaign_id: Union[int, str]
    ) -> Optional[GetMinerUniqueIdResponse]:
        """Retrieves the unique URL information for a given campaign ID.

        Args:
            campaign_id (Union[int, str]): The ID of the campaign.

        Returns:
            Optional[GetMinerUniqueIdResponse]: The unique URL information if it exists, None otherwise.
        """
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link/{campaign_id}_{self._hotkey}.json"
        try:
            with open(path, "r") as file:
                return GetMinerUniqueIdResponse.model_validate_json(
                    file.read()
                )
        except FileNotFoundError:
            bt.logging.error(
                prefix=LogLevel.LOCAL,
                msg=red(f"File not found by path: {path}"),
            )
        except:
            bt.logging.exception(
                prefix=LogLevel.LOCAL,
                msg=red(f"File broken by path: {path}"),
            )

    @staticmethod
    def get_cold_key(hotkey: str):
        """Retrieves the cold key for a given hotkey from a temporary file.

        Args:
            hotkey (str): The hotkey identifier.

        Returns:
            Union[dict, bool]: The cold key data if found, False otherwise.
        """
        try:
            with open(f"./tmp/{hotkey}.txt", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return False

    @staticmethod
    def save_cold_key(hotkey: str, cold_key: dict):
        """Saves the cold key data for a given hotkey to a temporary file.

        Args:
            hotkey (str): The hotkey identifier.
            cold_key (dict): The cold key data to save.
        """
        path = f"./tmp/{hotkey}.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(cold_key, file, indent=4)
