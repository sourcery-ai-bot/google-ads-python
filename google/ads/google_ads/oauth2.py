# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A set of functions to help initialize OAuth2 credentials."""


import functools

from google.oauth2.service_account import Credentials as ServiceAccountCreds
from google.oauth2.credentials import Credentials as InstalledAppCredentials
from google.auth.transport.requests import Request

from google.ads.google_ads import config

_SERVICE_ACCOUNT_SCOPES = ['https://www.googleapis.com/auth/adwords']
_DEFAULT_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'


def _initialize_credentials_decorator(func):
    """A decorator used to easily initialize credentials objects.

    Returns:
        An initialized credentials instance
    """
    @functools.wraps(func)
    def initialize_credentials_wrapper(*args, **kwargs):
        credentials = func(*args, **kwargs)
        credentials.refresh(Request())
        return credentials
    return initialize_credentials_wrapper


@_initialize_credentials_decorator
def get_installed_app_credentials(
    client_id, client_secret, refresh_token, token_uri=_DEFAULT_TOKEN_URI):
    """Creates and returns an instance of oauth2.credentials.Credentials.

    Args:
        client_id: A str of the oauth2 client_id from configuration.
        client_secret: A str of the oauth2 client_secret from configuration.
        refresh_token: A str of the oauth2 refresh_token from configuration.

    Returns:
        An instance of oauth2.credentials.Credentials
    """
    return InstalledAppCredentials(
        None, client_id=client_id, client_secret=client_secret,
        refresh_token=refresh_token, token_uri=token_uri)


@_initialize_credentials_decorator
def get_service_account_credentials(path_to_private_key_file, subject,
                                    scopes=_SERVICE_ACCOUNT_SCOPES):
    """Creates and returns an instance of oauth2.service_account.Credentials.

    Args:
        path_to_private_key_file: A str of the path to the private key file
            location.
        subject: A str of the email address of the delegated account.
        scopes: A list of additional scopes.

    Returns:
        An instance of oauth2.credentials.Credentials
    """
    return ServiceAccountCreds.from_service_account_file(
        path_to_private_key_file, subject=subject, scopes=scopes)


def get_credentials(config_data):
    """Decides which type of credentials to return based on the given config.

    Args:
        config_data: a dict containing client configuration.

    Returns:
        An initialized credentials instance.
    """
    required_installed_app_keys = config.get_oauth2_installed_app_keys()
    required_service_account_keys = config.get_oauth2_service_account_keys()

    if all(key in config_data for key in required_installed_app_keys):
        # Using the Installed App Flow
        return get_installed_app_credentials(
            config_data.get('client_id'),
            config_data.get('client_secret'),
            config_data.get('refresh_token'))
    elif all(key in config_data for key in required_service_account_keys):
        # Using the Service Account Flow
        return get_service_account_credentials(
            config_data.get('path_to_private_key_file'),
            config_data.get('delegated_account'))
    else:
        raise ValueError(
            f'Your YAML file is incorrectly configured for OAuth2. You need to define credentials for either the OAuth2 installed application flow ({required_installed_app_keys}) or service account flow ({required_service_account_keys}).'
        )
