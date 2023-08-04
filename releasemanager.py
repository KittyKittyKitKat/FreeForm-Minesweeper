# Copyright © Simon Harris-Palmer 2023. All rights reserved.

import json
from pathlib import Path
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
        self.version = 'v2.0.0'

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
        tags: list[str] = sorted(
            release['tag_name'].rpartition('-')[2] for release in github_release_data
        )
        return tags

    def is_release_up_to_date(self) -> bool:
        """Compare release to most up to date.

        Returns:
            The release is up to date.
        """
        try:
            tags = self.get_release_tags(self.github_api_releases_url)
        except LookupError:
            return True
        try:
            newest_release = tags[-1]
        except IndexError:
            return True
        return newest_release == self.version

    def outdated_notice(self, force_message: bool = False) -> None:
        """Display pop up message detailing release is out of date."""
        if (not force_message) and Path('ood_seen').is_file():
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
