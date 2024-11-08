# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------

from __future__ import annotations
from collections import defaultdict
import inspect
from pathlib import Path
import re
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Pattern,
    TypeVar,
    Union,
    get_type_hints,
)

from ._flag import Flag
from ._repeatable import Repeatable
from ._sticky import Sticky

DEFAULT_HELP_PARAMETERS = ["-h", "--help"]

T = TypeVar("T")
Argv = List[str]


def main(cli: Callable[[Argv], int]) -> None:
    """
    Calls the given CLI or subcommand and handles the method's return value as an exit code.

    Args:
        cli:
            The CLI or subcommand to run, which will be assumed to return an exit code.
    """
    import sys

    sys.exit(cli(sys.argv[1:]))


class Cli:

    def __init__(  # pylint: disable=too-many-branches
        self,
        method: Callable[..., int],
        aliases: Dict[str, str] | None = None,
        constructors: Dict[str, Union[Callable[[str], Any], Repeatable, Flag]] | None = None,
        deindentDocstring: int | None = None,
        helpParameters: List[str] | None = None,
        autoAliases: bool = False,
        caseInsensitive: bool = False,
        disableRequiredCheck: bool = False,
    ) -> None:
        """
        Uses the signature and docstring of the given method to generate a command line interface.

        Args:
            method:
                The method to generate a CLI for.

            aliases:
                A mapping of alias>parameterName. Do not include dashes. All aliases are single dash
                parameters, but are not limited to a single character.

            constructors:
                A mapping of parameter name to constructor method, that should output the type
                required by the corresponding method parameter. Also available are the special
                constructors `Repeatable`, `Sticky`, and `Flag`.

            deindentDocstring:
                Number of spaces to deindent the docstring by. If None, will be procedurally
                determined based on the number of spaces in front of the first line of the
                docstring.

            helpParameters:
                List of parameters that if given will immediately display the help and exit. Include
                a single or double dash to differentiate between aliases and regular parameters.
                If no value is received, it will default to `-h`, `--help`

            autoAliases:
                Generates aliases automatically by using the first still available letter for each
                kwarg. Will only generate aliases for kwargs that don't already have one. If all
                letters of the kwarg are already used, no alias will be made for it.

            caseInsensitive:
                All parameters will be lower cased before comparisons. Note that only user input is
                case insensitive, configuration is still case sensitive.

            disableRequiredCheck:
                Disables the check for required parameters.
                This is useful if the method required arguments are defined by a wrapper function.

        Returns:
            A function that can parse command line parameters (where the script path is expected to
            be removed) and return the output of the given method.
        """
        self.method = method
        self.aliases = {} if aliases is None else aliases
        self.constructors = {} if constructors is None else constructors
        self.disableRequiredCheck = disableRequiredCheck
        self.helpParameters = (
            helpParameters if helpParameters is not None else DEFAULT_HELP_PARAMETERS
        )
        self.caseInsensitive = caseInsensitive
        self.signature = inspect.signature(self.method, follow_wrapped=True)
        self.programName = self.method.__name__

        # Calculate docstring deindentation if not provided
        if deindentDocstring is None:
            self.deindentDocstring = 0
            doc = self._get_doc(method)
            if doc is not None:
                for char in doc:
                    if char in " \t":
                        self.deindentDocstring += 1
                    elif char not in "\r\n":
                        break
        else:
            self.deindentDocstring = None

        # Auto aliases
        if autoAliases:
            aliasedParams = set(alias for alias in self.aliases.values())
            paramNames = [
                param.name
                for param in self.signature.parameters.values()
                if param.name not in aliasedParams and param.default != param.empty
            ]

            # Add alias for each parameter by using the first available letter
            for paramName in paramNames:
                for char in paramName:
                    char = char.lower()
                    if char not in self.aliases and f"-{char}" not in self.helpParameters:
                        self.aliases[char] = paramName
                        break

        # Big list of all -a and --kwargs for easy kwarg check later
        self.dashKwargs = []
        for kwarg in self.signature.parameters.keys():

            # Args with no defaults are positional only
            if self.signature.parameters[kwarg].default == self.signature.parameters[kwarg].empty:
                if isinstance(self.constructors.get(kwarg), Flag):
                    raise ValueError(
                        f"Parameter '{kwarg}' must have a default to use the Flag constructor"
                    )
                continue
            if self.caseInsensitive:
                kwarg = kwarg.lower()
            kwarg = f"--{kwarg}"
            if kwarg in self.dashKwargs:
                raise ValueError(f"Duplicate parameter '{kwarg}'")
            self.dashKwargs.append(kwarg)

        # Aliases
        for alias, target in self.aliases.items():
            if self.signature.parameters[target].default == self.signature.parameters[target].empty:
                raise ValueError(f"Cannot make alias for positional parameter '{target}'")
            if self.caseInsensitive:
                alias = alias.lower()
            alias = f"-{alias}"
            if alias in self.dashKwargs:
                raise ValueError(f"Duplicate parameter '{alias}'")
            self.dashKwargs.append(alias)

        # Help
        self.dashHelp = []
        for alias in self.helpParameters:
            if self.caseInsensitive:
                alias = alias.lower()
            if alias in self.dashKwargs:
                raise ValueError(f"Help parameter duplicate '{alias}'")
            self.dashKwargs.append(alias)
            self.dashHelp.append(alias)

    @classmethod
    def _get_doc(cls, method) -> Optional[str]:
        """Gets the docstring of a method/function with support for wrapping and inheritance."""
        import inspect

        if doc := inspect.getdoc(method):
            return doc
        if hasattr(method, "__wrapped__"):
            return cls._get_doc(method.__wrapped__)
        return doc

    def help(self, extra: Optional[str] = None, exitCode: int = 1) -> None:
        """
        Generate cli help information and exit the application.

        Args:
            extra:
                Additional help information.

            exitCode:
                Exit code.
        """
        # Deindented docstring
        doc = self._get_doc(self.method)
        if doc is not None:
            print(
                "\n".join(
                    l[self.deindentDocstring :]
                    for l in doc.lstrip("\r\n").rstrip("\r \n").split("\n")
                ),
            )

        # Index aliases
        paramShortcuts = defaultdict(list)
        for shortcut, paramName in self.aliases.items():
            paramShortcuts[paramName].append(shortcut)

        # Method signature
        print(
            f"\n\nCommand line parameters: (case {'in' if self.caseInsensitive else ''}sensitive)"
            f"\n\n{self.programName}("
        )
        typingPattern = re.compile(r"(?<=[^a-zA-Z])typing\.(?=[A-Z])")
        for param in self.signature.parameters.values():
            self._print_parameter_help(param, typingPattern, paramShortcuts)
        print(")", end="\n")

        # Extras
        if extra:
            print("\n" + extra, end="\n")

        # Exit if required
        if exitCode is not None:
            import sys

            sys.exit(exitCode)

    def _print_parameter_help(
        self,
        param: inspect.Parameter,
        typingPattern: Pattern[str],
        paramShortcuts: Dict[str, List[Any]],
    ) -> None:
        paramDoc = "    "

        # Aliases
        if param.default == param.empty:
            paramDoc += param.name
        else:
            paramDoc += " | ".join(
                [f"-{s}" for s in paramShortcuts[param.name]] + [f"--{param.name}"]
            )

        # Type from constructor
        typeDoc = None
        if param.name in self.constructors:
            constructor = self.constructors[param.name]
            if isinstance(constructor, Repeatable):
                typeDoc = self._get_doc(constructor.constructor)
            elif not isinstance(constructor, (type, Flag)):
                typeDoc = self._get_doc(constructor)
            if typeDoc:
                typeDoc = f'<"{typeDoc}">'

        # Type from annotation, remove "typing." because it's ugly
        if typeDoc is None and param.annotation != param.empty:
            typeDoc = typingPattern.sub(
                "", f"<{getattr(param.annotation, '__name__', param.annotation)}>"
            )

        # Add to doc
        if typeDoc is not None:
            paramDoc += f" {typeDoc}"

        # Details
        detailsDocs = []

        # Special constructors
        if isinstance(self.constructors.get(param.name), (Flag, Repeatable, Sticky)):
            detailsDocs.append(self.constructors[param.name].__class__.__name__.lower())

        # Default
        detailsDocs.append(
            f"default: {repr(param.default)}" if param.default != param.empty else "required"
        )

        # Add details
        if detailsDocs:
            paramDoc += f" ({', '.join(detailsDocs)})"

        # Print
        print(paramDoc)

    def _get_required_parameters(self):
        required = set()
        for param in self.signature.parameters.values():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                raise ValueError("*args and **kwargs are not currently supported")
            if param.default == param.empty:
                required.add(param.name)
        return required

    def main(self) -> None:
        """Uses sys.argv to call this CLI."""
        import sys

        sys.exit(self(sys.argv))

    def __call__(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        self, argv: Argv
    ) -> int:
        # Don't modify argv
        argv = list(argv)
        self.programName = Path(argv.pop(0)).name

        # Get signature of method
        hints = get_type_hints(self.method)

        # Index args by position
        positional = list(self.signature.parameters.keys())

        # Validate signature is supported and list required parameters
        required = self._get_required_parameters()

        # Keep track of where kwargs begin
        argIndex = 0
        kwargIndex = len(positional)

        # Parse args and kwargs
        accumulator = None
        kwargs = {}
        while len(argv) > 0:
            arg = argv.pop(0)
            values = []

            # Keyword args
            if (arg.lower() if self.caseInsensitive else arg) in self.dashKwargs:

                # Short circuit help
                if (arg.lower() if self.caseInsensitive else arg) in self.dashHelp:
                    self.help()

                paramName = self.aliases[arg[1:]] if arg[1:] in self.aliases else arg[2:]

                # Check if already supplied in positionals
                if paramName in positional[:argIndex]:
                    self.help(f"Parameter '{paramName}' already provided by positional parameters")

                # Update kwargIndex to prevent positional args from being supplied after kwargs
                kwargIndex = min(positional.index(paramName), kwargIndex)

                # Disable accumulator
                accumulator = None

            # Positional args
            else:

                # Positional args
                if accumulator is None:
                    if argIndex > len(positional):
                        self.help(f"Unrecognized parameter '{arg}'")
                    paramName = positional[argIndex]
                    if paramName in kwargs and not isinstance(
                        self.constructors.get(paramName), Repeatable
                    ):
                        self.help(f"Parameter '{paramName}' already provided by keyword parameters")
                    if isinstance(self.constructors.get(paramName), Flag):
                        self.help(f"Parameter '{paramName}' must be passed as a flag")
                    values.append(arg)

                # Honor accumulator
                else:
                    paramName = accumulator

                    # Put arg back in argv so it can be popped
                    argv = [arg] + argv

            # Find constructor
            constructor = (
                self.constructors[paramName] if paramName in self.constructors else hints[paramName]
            )

            # Repeatable param count
            if isinstance(constructor, Repeatable):
                count = constructor.tupleLength

                # Begin accumulating
                if isinstance(constructor, Sticky):
                    accumulator = paramName

            # Flag param
            elif isinstance(constructor, Flag):
                kwargs[paramName] = not self.signature.parameters[paramName].default
                continue

            # Non-repeatable param count
            else:
                if paramName in kwargs:
                    self.help(f"Parameter '{paramName}' is already provided")
                try:
                    count = len(inspect.signature(constructor))  # type: ignore # linter bug
                except Exception:  # pylint: disable=broad-except
                    count = 1

                # Increment argIndex for non-repeatable positional parameters
                if len(values) > 0:
                    argIndex += 1
            try:
                values.extend([argv.pop(0) for _ in range(count - len(values))])
            except IndexError:
                self.help(f"Parameter '{paramName}' requires {count} values")

            # Convert to final value
            try:
                value = constructor(*values)
            except Exception as exc:  # pylint: disable=broad-except
                import traceback

                annotation = self.signature.parameters[paramName].annotation
                name = getattr(annotation, "__name__", annotation)
                self.help(
                    "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                    + f"\nParameter '{paramName}'"
                    + f" unable to convert {values} to '{getattr(name, '__name__', name)}': {exc}"
                )
            # Add to kwargs
            else:
                kwargs[paramName] = value

        # Check if all params without defaults have been set
        missing = required - set(kwargs)
        if missing and not self.disableRequiredCheck:
            self.help(f"Missing {len(missing)} required parameters: {list(missing)}")

        # Finalize any repeatable kwargs
        for key, value in kwargs.items():
            if isinstance(value, Repeatable):
                kwargs[key] = value.construct(value.items)

        # Run the method using the compiled args/kwargs and return its result
        return self.method(**kwargs)
