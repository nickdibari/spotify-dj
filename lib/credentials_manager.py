import json

import config


class CredentialsManager(object):
    """Helper class for managing credential file for Spotify auth"""

    @staticmethod
    def read_credentials_file() -> dict:
        """
        Read the contents of the credentials files and return the data
        from it.

        Fields:
            access_token (str)
            refresh_token (str)
            last_refreshed (str)

        :return: (dict) Spotify credentials data
        """
        with open(config.SPOTIFY_CREDENTIALS_FILE) as fp:
            return json.load(fp)

    @staticmethod
    def update_credentials_file(data) -> None:
        """
        Update the contents of the credentials file.

        :param data: (dict) Spotify credentials data
        """
        with open(config.SPOTIFY_CREDENTIALS_FILE, 'w') as fp:
            json.dump(data, fp)
