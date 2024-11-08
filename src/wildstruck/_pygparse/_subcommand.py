# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------

from __future__ import annotations
from pathlib import Path
from typing import Callable, Dict, List, Optional, TypeVar


T = TypeVar("T")


Argv = List[str]


class Subcommand:
    def __init__(
        self,
        commandMap: Dict[str, Callable[[Argv], int]],
        commandHelp: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        caseSensitive: bool = True,
    ) -> None:
        """
        Parses a single positional argument as a subcommand. The first positional argument is going
        to be consumed, and the Callable will be called with the remaining arguments.

        Args:
            commandMap:
                A mapping of command to methods, which can be `cli`, `subcommand`, or any method
                that accepts the truncated argv.

            commandHelp:
                A short description of each command.

            description:
                A descriptive text that will be displayed in the help for this subcommand, before
                the listing of available commands.

            caseSensitive:
                All parameters will be lower cased before comparisons.

        Returns:
            The return value of the Callable that is ultimately executed.
        """
        self.commandMap = (
            commandMap if caseSensitive else {k.lower(): v for k, v in commandMap.items()}
        )
        self.commandHelp = commandHelp or {}
        self.description = description
        self.caseSensitive = caseSensitive

    def commands_string(self, indent: int = 4) -> List[str]:
        """
        Get the command as a string.

        Args:
            indent:
                Command indentation.

        Returns:
            List of command strings.
        """
        output = []
        for name, command in self.commandMap.items():
            output.append(
                f"- {name}"
                # Command summary
                f"{(': ' + self.commandHelp.get(name, '')) if name in self.commandHelp else ''}"
            )
            if isinstance(command, Subcommand):
                output.append(" " * indent + f"{name} subcommands:")
                output.extend([" " * indent + c for c in command.commands_string(indent)])
        return output

    def help(self, message: str | None = None) -> None:
        """
        Print the command help message and exit the application.

        Args:
            message:
                Message to include with the help information.
        """
        import sys

        if self.description:
            print(self.description, end="\n\n")
        if message:
            print(message)
        print(
            f"Please choose a command from the list"
            f" (case {'' if self.caseSensitive else 'in'}sensitive):"
        )
        print("\n".join([" " + c for c in self.commands_string()]))
        sys.exit(1)

    def main(self) -> None:
        """Uses sys.argv to call this subcommand."""
        import sys

        sys.exit(self(sys.argv))

    def __call__(self, argv: Argv) -> int:

        # Do not modify original args
        argv = list(argv)
        programName = Path(argv.pop(0)).name

        # Check that command is provided
        try:
            arg = argv.pop(0)
        except IndexError:
            # Help should call sys.exit
            self.help()
            return 1

        # Case sensitivity
        commandName = arg if self.caseSensitive else arg.lower()

        # Check that command exists
        try:
            command = self.commandMap[commandName]
        except KeyError:
            # Help should call sys.exit
            self.help(f"Invalid command '{arg}'")
            return 1

        # Add subcommand name to argv for Cli's help
        return command([f"{programName} {commandName}"] + argv)
