# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------
# The code contained within this file and all other files with the above notice is used in this
# repository through an exclusive licensing agreement between Fred Dufresne and Botni.Vision, Inc.
#
# Acquiring the code grants usage permission according to the overarching repository license, but
# does not grant permission to copy, modify, or distribute the code or derivatives of the code
# outside of the scope of this repository.
# ----------------------------------------------------------------------------------------------


from . import parsers
from ._cli import Cli, main
from ._flag import Flag
from ._repeatable import Repeatable
from ._sticky import Sticky
from ._subcommand import Subcommand
