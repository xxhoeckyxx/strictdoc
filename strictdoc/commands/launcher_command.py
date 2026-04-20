"""Launcher command for the Tk-based StrictDoc UI."""

import argparse
import os

from strictdoc.cli.base_command import BaseCommand
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.launcher import main as launcher_main


class LauncherCommand(BaseCommand):
    HELP = "Launch StrictDoc's desktop launcher (experimental)."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:  # noqa: ARG003
        parser.add_argument(
            "workspace",
            nargs="?",
            help=(
                "Optional StrictDoc workspace directory to preselect in the "
                "launcher (use '.' for the current working directory)."
            ),
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        # Resolve optional workspace argument (including '.' for CWD).
        workspace_arg = getattr(self.args, "workspace", None)
        workspace: str | None
        if isinstance(workspace_arg, str) and workspace_arg.strip():
            workspace = os.path.abspath(workspace_arg)
        else:
            workspace = None

        # Delegate to the Tkinter launcher entry point.
        launcher_main(workspace)
