import json
from itertools import groupby
from pathlib import Path
from platform import system
from tkinter import Toplevel
from urllib.request import urlopen

from dialogues import AcknowledgementDialogue, AcknowledgementWithLinkDialogue


class ReleaseManager:
    """Provide utilities for checking current release against the most up to date release.

    Attributes:
        github_api_releases_url: URL to fetch data from.
        github_releases_url: URL to releases page for project.
        platform: The OS of the system the program is running on.
        version: The version of the code, shipped with releases.
    """

    def __init__(self, parent: Toplevel) -> None:
        self.parent = parent
        self.github_api_releases_url = 'https://api.github.com/repos/KittyKittyKitKat/FreeForm-Minesweeper/releases'
        self.github_releases_url = (
            'https://github.com/KittyKittyKitKat/FreeForm-Minesweeper/releases'
        )
        self.platform = system()

        # This is a dummy value for the purpose of source code.
        # The releases will have the proper information contained within.
        # This information will directly correlate to the release info on GitHub.
        self.version = 'vX.X.X'

    def get_release_tags(self, url: str) -> list[str]:
        """Fetch the releases tags from GitHub's repo API.

        Args:
            url: Url pointing to the API JSON for GitHub releases.

        Raises:
            LookupError, if response could not be read or parsed.

        Returns:
            A list of all the release tags for the OS the game is running on.
        """
        try:
            with urlopen(url) as response:
                github_release_data = json.loads(response.read())
        except:
            AcknowledgementDialogue(
                self.parent,
                'Could not fetch release data. You can safely ignore this message.',
                title='HTTP Error',
            )
            raise LookupError()
        tags = [release['tag_name'] for release in github_release_data]
        tags_linux, tags_windows = [
            list(g) for _, g in groupby(sorted(tags), key=lambda s: s[0])
        ]
        if self.platform == 'Linux':
            return tags_linux
        elif self.platform == 'Windows':
            return tags_windows
        else:
            return []

    def is_release_up_to_date(self) -> bool:
        """Compare release to most up to date.

        Returns:
            True if the version is the most recent, or is the development dummy version.
            False otherwise.
        """
        if self.version == 'vX.X.X':
            return True
        try:
            tags = self.get_release_tags(self.github_api_releases_url)
        except LookupError:
            return True
        if tags == [] and not Path('os_fetch_seen').is_file():
            AcknowledgementDialogue(
                self.parent,
                (
                    'Could not retrieve operating system information to queue updates.\n'
                    'You can safely ignore this message.'
                ),
                title='OS Fetching Error',
            )
            Path('os_fetch_seen').touch()
            return True
        up_to_date_release = tags[-1]
        current_release = self.platform + '-' + self.version
        return up_to_date_release == current_release

    def outdated_notice(self) -> None:
        """Display pop up message detailing release is out of date."""
        if Path('ood_seen').is_file():
            return
        AcknowledgementWithLinkDialogue(
            self.parent,
            (
                f'This release may not be up to date, '
                'and as such you may be missing out on important new features or bug fixes.\n'
                f'Please go to link below to download and install the latest release.'
            ),
            ('Releases Page', self.github_releases_url),
            title='Outdated Release',
        )
        Path('ood_seen').touch()