"""Utilities specific to CodeRed deployments."""

import os

from cr import api

from django_simple_deploy.management.commands.utils.command_errors import (
    DSDCommandError,
)
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config


def get_cr_project_status(cr_project_name, raw=False):
    """Get status of the user's project.

    Can be used to get deployed URL, and also to validate the provided project
    name.

    Returns:
        Dict: JSON dict representing project.
        Tuple: If raw=True, return tuple including status and project info dict.
    """
    url = f"/api/webapps/{cr_project_name}/"
    cr_token = os.environ.get("CR_TOKEN")
    response = api.coderedapi(url, "GET", cr_token)

    # Index 0 is status code, index 1 is actual dict.
    if raw:
        return response
    else:
        return response[1]

def get_deployed_project_url(cr_project_name):
    """Get the URL of the deployed project."""
    status_dict = get_cr_project_status(cr_project_name)
    return status_dict["primary_url"]

def validate_project_name(cr_project_name):
    """Make sure provided cr project name is valid.

    Returns:
    - None: if project name is valid.
    Raises:
    - DSDCommandError: if project name is invalid.
    """
    if dsd_config.unit_testing:
        return

    try:
        get_cr_project_status(cr_project_name, raw=True)
    except Exception as e:
        # The API raises a simple Exception with a custom message; don't catch other
        # more general exceptions.
        # DEV: Probably want to move this check to `get_cr_project_status()`.
        if str(e) == "Invalid token.":
            msg = "Missing or invalid token for the CodeRed API. Please run the following command:"
            msg += "\n  $ export CR_TOKEN=<api-token>"
            msg += "\nReplace <api-token> with the value of your CodeRed API token."
            msg += "\nAfter exporting your API token, try running deploy again."
        else:
            msg = f'The project "{cr_project_name}" does not seem to be a valid project name.'
            msg += "\n\nIf this is a typo, please run the deploy command again."
            msg += "\nIf you haven't created a project in the CodeRed admin panel yet, please"
            msg += "\n  do that and then run deploy again."

        raise DSDCommandError(msg)
