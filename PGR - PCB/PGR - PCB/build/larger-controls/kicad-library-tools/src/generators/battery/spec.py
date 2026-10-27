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

from generators.tools.footprint.standard_box_generator import StandardBoxSpec
from generators.tools.spec.base_spec import BaseSpec
from generators.tools.spec.spec_registry import register_spec


@register_spec
class BatterySpec(StandardBoxSpec):
    """A standard-box specification for battery holders."""


def create_specs(file_name: str, generator_name: str) -> list[BaseSpec]:
    """Create the specs for the battery generator.

    Battery footprints use the standard-box spec. The 3D models are still
    defined by the legacy CadQuery definitions in cq_parameters.yaml, so they
    are returned here as `LegacyModelSpec`s alongside the footprint specs.

    Args:
        file_name: The name of the specs file to create the specs from.
        generator_name: The name of this generator.

    Returns:
        The footprint and model specs for the generator.
    """
    from generators.tools.spec import legacy_model_spec
    from generators.tools.spec.spec_generator import get_specs

    specs: list[BaseSpec] = list(get_specs(None, file_name, BatterySpec))
    specs += legacy_model_spec.create_specs(generator_name)
    return specs
