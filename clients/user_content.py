import requests

from clients.base import VersionClient, BaseHTTPClient
from helpers.constants import paths


class GitHubUserContentVersionClient(VersionClient, BaseHTTPClient):
    def get_version(self) -> str:
        response = requests.get(
            self._base_url + paths.GitHubUserContentPaths.VERSION
        )
        return response.text
