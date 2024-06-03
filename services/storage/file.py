import json
import os
from typing import Union, Optional

import bittensor as bt

from helpers.constants import Const
from helpers.constants.colors import colorize, Color, red, yellow, magenta
from helpers.logging import LogLevel
from schemas.bit_ads import Score, GetMinerUniqueIdResponse, Aggregation
from services.storage.base import BaseStorage


class FileStorage(BaseStorage):
    def __init__(
        self, neuron_type: str, hotkey: str, root_dir: str = Const.ROOT_DIR
    ):
        self._root_dir = root_dir
        self._hotkey = hotkey
        self._neuron_type = neuron_type
        self._create_dirs()

    def _create_dirs(self):
        directories = [
            self._root_dir,
            f"{self._root_dir}/{self._neuron_type}",
            f"{self._root_dir}/{self._neuron_type}/{self._hotkey}",
            f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/campaign_id",
            f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link",
        ]

        if self._neuron_type == Const.VALIDATOR:
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

    def save_campaign(self, task: GetMinerUniqueIdResponse):
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/campaign_id/{task.product_unique_id}.json"
        with open(path, "w") as file:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=colorize(Color.YELLOW, f"Save campaign to: {path}"),
            )
            file.write(task.json(indent=4))

    def remove_campaign(self, campaign_id: Union[int, str]):
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/campaign_id/{campaign_id}_{self._hotkey}.json"
        if os.path.exists(path):
            os.remove(path)
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=colorize(Color.YELLOW, "Remove campaign file: {path}"),
            )

    def save_miner_unique_url(self, data: GetMinerUniqueIdResponse):
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link/{data.product_unique_id}_{self._hotkey}.json"
        with open(path, "w") as file:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=yellow(
                    f"Save campaign unique url to: {path}",
                ),
            )
            file.write(data.json(indent=4))

    def save_miner_unique_url_stats(self, data: Aggregation):
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link_stats/{data.product_unique_id}_{data.product_item_unique_id}.json"
        with open(path, "w") as file:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=yellow(
                    f"Save campaign unique url statistics to: {path}",
                ),
            )
            file.write(data.json(indent=4))

    def save_miner_unique_url_score(
        self,
        product_unique_id: Union[int, str],
        product_item_unique_id: Union[int, str],
        data: Score,
    ):
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link_score/{product_unique_id}_{product_item_unique_id}.json"
        with open(path, "w") as file:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=yellow(
                    f"Save campaign unique url score to: {path}",
                ),
            )
            file.write(data.json(indent=4))

    def unique_link_exists(self, campaign_id: Union[int, str]):
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link/{campaign_id}_{self._hotkey}.json"
        return os.path.exists(path)

    def get_unique_url(
        self, campaign_id: Union[int, str]
    ) -> Optional[GetMinerUniqueIdResponse]:
        path = f"{self._root_dir}/{self._neuron_type}/{self._hotkey}/unique_link/{campaign_id}_{self._hotkey}.json"
        try:
            return GetMinerUniqueIdResponse.parse_file(path)
        except FileNotFoundError:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=red(f"File not found by path: {path}"),
            )
        except:
            bt.logging.info(
                prefix=LogLevel.LOCAL,
                msg=red(f"File broken by path: {path}"),
            )

    @staticmethod
    def get_cold_key(hotkey):
        try:
            with open(f"./tmp/{hotkey}.txt", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return False

    @staticmethod
    def save_cold_key(hotkey, cold_key):
        path = f"./tmp/{hotkey}.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(cold_key, file, indent=4)
