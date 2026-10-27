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

import dataclasses


@dataclasses.dataclass
class Datasheet:
    url: str | None
    """The datasheet for the part"""

    page: int | None
    """The page number of the datasheet to refer to. None if the
    whole datasheet is relevant, or if no datasheet is specified."""

    def construct_url(self) -> str | None:
        """The complete URI to the datasheet, including the page number if
        specified. If no datasheet is specified, returns None."""

        if self.url is None:
            return None

        if self.page is not None:
            return f"{self.url}#page={self.page}"

        return self.url


class CommonMetadata:
    """
    Class that reads "standard" metadata out of a dict, probably
    from YAML and puts a typed interface on it.

    This avoids every generator having to define its own reading
    and validation for things that are common to all footprints.

    Individual generators can still define their own metadata,
    and can opt to ignore or override this class if it's somehow
    not suitable, and can impose their own requirements (like saying
    datasheets are mandatory). Basically this calls just standardised
    the datatypes and the dict keys/layouts.
    """

    datasheets: list[Datasheet]
    """The datasheets for the footprint. Most footprints will have one
    of these, but some generators may generate the URL otherwise. Parts
    can have multiple datasheets."""

    description: str | None
    """A description of the footprint. Most generators will generate this
    but some may allow or expect it to be set by the YAML. They may still
    append or otherwise modify it."""

    manufacturer: str | None
    """Some footprints are manufacturer-specific, annd may define this."""

    part_number: str | None
    """Some footprints are unique to a particular part number (MPN)"""

    additional_tags: list[str]
    """
    A list of additional keywords that can be used to search for this footprint
    in the KiCad UI.
    Note: "tags" is a bad name, these are _search keywords_. But all the YAML uses
    "tags", so changing it only here would be more confusing."""

    compatible_mpns: list[str]
    """A list of compatible MPNs (i.e. other manufacturer's part numbers,
    drawing numbers, standards, etc) that this footprint is compatible with."""

    custom_name_format: str | None
    """Set if the footprint def defines its own name format
    Actually applying this format (and which variables it has) is the
    responsibility of the generator."""

    library_name: str | None
    """Set if the footprint def defines its own library name."""

    def __init__(self, spec: dict):

        self.description = spec.get("description", None)
        self.datasheets = self._init_datasheets(spec)

        self.manufacturer = spec.get("manufacturer", None)
        self.part_number = spec.get("part_number", None)

        self.additional_tags = spec.get("additional_tags", [])
        self.compatible_mpns = spec.get("compatible_mpns", [])

        self.custom_name_format = spec.get("custom_name_format", None)
        self.library_name = spec.get("library_name", spec.get("lib_name", None))

    @staticmethod
    def _init_datasheets(spec: dict) -> list[Datasheet]:

        datasheets: list[Datasheet] = []
        spec_node = spec.get("datasheet", spec.get("size_source", None))

        if spec_node is None:
            return datasheets

        # The simplest case is a single datasheet URL, with no page number
        # or a #page=N fragment.
        if isinstance(spec_node, str):
            datasheets.append(Datasheet(url=spec_node, page=None))
        else:
            # There are two options now: either `datasheet` is a
            # DS dict, or it's a list of DS dicts
            ds_nodes = spec_node if isinstance(spec_node, list) else [spec_node]
            for ds_node in ds_nodes:
                if not isinstance(ds_node, dict):
                    raise ValueError(
                        f"Invalid datasheet entry: {ds_node!r} (must be a dict)"
                    )
                # All datasheet dicts must have a 'url' key
                url = ds_node["url"]
                page = ds_node.get("page", None)
                datasheets.append(Datasheet(url=url, page=page))

        return datasheets

    @property
    def datasheet(self) -> str | None:
        """
        Compose all datasheet URLs into a single string
        """

        if not self.datasheets:
            return None

        strs = [ds.construct_url() for ds in self.datasheets]
        strs = [s for s in strs if s is not None]

        return ", ".join(strs) if strs else None
