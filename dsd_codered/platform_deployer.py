"""Manages all CodeRed-specific aspects of the deployment process.

Notes:
- 

Add a new file to the user's project, without using a template:

    def _add_dockerignore(self):
        # Add a dockerignore file, based on user's local project environmnet.
        path = sd_config.project_root / ".dockerignore"
        dockerignore_str = self._build_dockerignore()
        plugin_utils.add_file(path, dockerignore_str)

Add a new file to the user's project, using a template:

    def _add_dockerfile(self):
        # Add a minimal dockerfile.
        template_path = self.templates_path / "dockerfile_example"
        context = {
            "django_project_name": sd_config.local_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = sd_config.project_root / "Dockerfile"
        plugin_utils.add_file(path, contents)

Modify user's settings file:

    def _modify_settings(self):
        # Add platformsh-specific settings.
        template_path = self.templates_path / "settings.py"
        context = {
            "deployed_project_name": self._get_deployed_project_name(),
        }
        plugin_utils.modify_settings_file(template_path, context)

Add a set of requirements:

    def _add_requirements(self):
        # Add requirements for deploying to Fly.io.
        requirements = ["gunicorn", "psycopg2-binary", "dj-database-url", "whitenoise"]
        plugin_utils.add_packages(requirements)
"""

import sys, os, re, json
from pathlib import Path
import shutil

from django.utils.safestring import mark_safe

import requests

from . import deploy_messages as platform_msgs

from simple_deploy.management.commands.utils import plugin_utils
from simple_deploy.management.commands.utils.plugin_utils import sd_config
from simple_deploy.management.commands.utils.command_errors import (
    SimpleDeployCommandError,
)


class PlatformDeployer:
    """Perform the initial deployment to CodeRed

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and ...
    """

    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"

    # --- Public methods ---

    def deploy(self, *args, **options):
        """Coordinate the overall configuration and deployment."""
        plugin_utils.write_output("\nConfiguring project for deployment to CodeRed...")

        self._validate_platform()
        self._prep_automate_all()

        # Configure project for deployment to CodeRed.
        self._split_settings()
        self._modify_managepy()

        self._conclude_automate_all()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to CodeRed.

        Returns:
            None
        Raises:
            SimpleDeployCommandError: If we find any reason deployment won't work.
        """
        pass

    def _prep_automate_all(self):
        """Take any further actions needed if using automate_all."""
        pass

    def _split_settings(self):
        """Split settings.py into base.py and prod.py.

        CodeRed expects to find a settings/ dir, with at least a base.py and prod.py.
        The user's original settings.py file becomes base.py, and prod.py contains
        overrides.
        """
        # Add new settings dir, if it doesn't already exist.
        path_settings_dir = sd_config.settings_path.parent / "settings"
        if not path_settings_dir.exists():
            plugin_utils.write_output(
                f"\nAdding new settings/ directory at {path_settings_dir}..."
            )
            plugin_utils.add_dir(path_settings_dir)

        # Copy settings file to base.py.
        path_settings_base = path_settings_dir / "base.py"
        plugin_utils.write_output(f"  Copying settings.py to {path_settings_base}.")
        shutil.copy(sd_config.settings_path, path_settings_base)

        # Write prod settings. There's no custom data, so just copy the template file.
        path_settings_prod = path_settings_dir / "prod.py"
        plugin_utils.write_output(
            f"  Writing production settings to {path_settings_prod}."
        )
        path_prod_template = self.templates_path / "settings_prod.py"
        shutil.copy(path_prod_template, path_settings_prod)

        # Remove original settings.py file.
        plugin_utils.write_output(
            f"  Deleting original settings file: {sd_config.settings_path}"
        )
        sd_config.settings_path.unlink()
        sd_config.settings_path = None

    def _modify_managepy(self):
        """Update manage.py so it loads base settings, not prod.

        If you only split settings.py into base.py and prod.py, local runserver no longer
        works because it's using production settings.

        CodeRed seems to consistently set a CR_USER_UID env var. Make production settings
        dependent on this env var.
        """
        plugin_utils.write_output("Modifying manage.py to use local settings...")
        path_managepy = sd_config.project_root / "manage.py"

        # A template would be nicer, but I believe this approach is more resilient to
        # changes in manage.py across Django versions.
        lines = path_managepy.read_text().splitlines()

        new_lines = []
        for line in lines:
            if '.settings")' in line:
                new_lines.append('    if "CR_USER_UID" in os.environ:')
                new_lines.append(line.replace("os.environ", "    os.environ"))
                new_lines.append("    else:")
                new_lines.append(
                    line.replace('.settings")', '.settings.base")').replace(
                        "os.environ", "    os.environ"
                    )
                )
            else:
                new_lines.append(line)

        contents = "\n".join(new_lines)
        path_managepy.write_text(contents)

    def _conclude_automate_all(self):
        """Finish automating the push to CodeRed.

        - Commit all changes.
        - ...
        """
        # Making this check here lets deploy() be cleaner.
        if not sd_config.automate_all:
            return

        plugin_utils.commit_changes()

        # Push project.
        plugin_utils.write_output("  Deploying to CodeRed...")

        # Should set self.deployed_url, which will be reported in the success message.
        pass

    def _show_success_message(self):
        """After a successful run, show a message about what to do next.

        Describe ongoing approach of commit, push, migrate.
        """
        if sd_config.automate_all:
            msg = platform_msgs.success_msg_automate_all(self.deployed_url)
        else:
            msg = platform_msgs.success_msg(log_output=sd_config.log_output)
        plugin_utils.write_output(msg)
