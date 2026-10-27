# generators is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# generators is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# generators. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) The KiCad Librarian Team

import sys

from generators.tools.footprint.standard_box_generator import (
    StandardBoxSpec,
    create_footprints,
)
from generators.tools.spec.spec_generator import get_file_name_ids_specs


def main(generator_name: str, file_names: list[str]) -> int:
    """Generate the footprints for the given YAML files.

    Args:
        generator_name: The name of the generator.
        file_names: The list of YAML files to process.

    Returns:
        The number of footprints generated.
    """
    num_footprints_generated = 0
    for file_name in file_names:
        for _, ids_specs in get_file_name_ids_specs(None, file_name):
            for id, spec in ids_specs:
                spec_obj = StandardBoxSpec(id, spec, file_name)
                num_footprints_generated += create_footprints(spec_obj, generator_name)
    return num_footprints_generated


if __name__ == "__main__":
    main("bridge_rectivier_NOT_PORTED", sys.argv[1:])
