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

from math import sqrt

from generators.tools.footprint.drawing_tools import applyKeepouts
from generators.tools.footprint.drawing_tools_silk import (
    SilkArrowSize,
    draw_silk_triangle_in_corner,
)
from generators.tools.footprint.nodes import pin1_arrow
from KicadModTree import (
    ExposedPad,
    PadArray,
    shape_to_node,
)
from KicadModTree.nodes.specialized.PadArray import find_lowest_numbered_pad
from kilibs.config import global_config as GC
from kilibs.geom import (
    BoundingBox,
    Direction,
    GeomRectangle,
    GeomShapesClosed,
    Vector2D,
)
from kilibs.geom.operations import subtract

from .footprint_layout import CourtyardStyle, FabStyle, FootprintLayout


class QfnLayout(FootprintLayout[GeomRectangle, PadArray | ExposedPad]):
    """This layout is typically used by four-sided nolead packages:

    .. aafig::

                       +---+  +---+
                       |   |  |   |
                 /-----+---+--+---+------+
                /      |   |  |   |      |
            +---+---+  +---+  +---+  +---+---+
            |   |   |                |   |   |
            +---+---+   +--------+   +---+---+
                |       |   EP   |       |
            +---+---+   +--------+   +---+---+
            |   |   |                |   |   |
            +---+---+  +---+  +---+  +---+---+
                |      |   |  |   |      |
                +------+---+--+---+------+
                       |   |  |   |
                       +---+  +---+

    The pad arrays and the optional exposed pad are not defined in the
    this class, but injected to the constructor.

    This differs from the `DualAndQuadPadArrayLayout` in that it has
    different silkscreen heuristics. Additionally it may have other
    QFN-specific parameters.
    """

    # Class attributes:
    SMALL_ARROW_CUTOFF = 2.0

    def __init__(
        self,
        global_config: GC.GlobalConfig,
        courtyard_offset_body: float,
        courtyard_offset_pads: float,
        pad_arrays: list[PadArray],
        exposed_pad: ExposedPad | None,
        body_size: Vector2D,
        footprint_name: str,
    ) -> None:
        """
        Create a QFN layout.

        The body is centered at the origin.

        Args:
            global_config: The global config object.
            courtyard_offset_body: The clearance between the courtyard and the component
                body.
            courtyard_offset_pads: The clearance between the courtyard and the pads.
            pad_arrays: The pads.
            exposed_pad: The optional exposed pad.
            body_size: The nominal size of the body, in mm.
            footprint_name: The name of the footprint.
        """
        # Instance attributes:
        self.pad_arrays: list[PadArray]
        """The list of the 4 pad arrays of the footprint."""
        self.exposed_pad: ExposedPad | None
        """Optional exposed pad."""
        self.body_size: Vector2D
        """The nominal size of the rectangular body, in mm."""
        self.courtyard_offset_body: float
        """Offset between the courtyard and the component body."""
        self.courtyard_offset_pads: float
        """Offset between the courtyard and the pads."""

        self.pad_arrays = pad_arrays
        self.exposed_pad = exposed_pad
        self.body_size = body_size
        self.courtyard_offset_body = courtyard_offset_body
        self.courtyard_offset_pads = courtyard_offset_pads

        super().__init__(
            global_config=global_config,
            pads=pad_arrays + [exposed_pad] if exposed_pad is not None else pad_arrays,
            body_shape=GeomRectangle(center=Vector2D.zero(), size=self.body_size),
        )

        self._add_automatic_fab_outline(FabStyle.CHAMFER_RECT)
        self._add_automatic_courtyard(CourtyardStyle.TIGHT)
        self._add_automatic_labels(footprint_name)
        self._create_silk()

    def _get_courtyard_offset_pads(self) -> float | GC.GlobalConfig.CourtyardType:
        """Return the courtyard offset for the pads."""
        return self.courtyard_offset_pads

    def _get_courtyard_offset_body(self) -> float | GC.GlobalConfig.CourtyardType:
        """Return the courtyard offset from the body."""
        return self.courtyard_offset_body

    def _get_top_pad_array(self) -> PadArray | None:
        """Get the top pad array."""
        for pad_array in self.pad_arrays:
            bbox = pad_array.bbox()
            if pad_array.spacing.x and bbox.is_defined() and bbox.center.y < 0:
                return pad_array
        return None

    def _get_left_pad_array(self) -> PadArray | None:
        """Get the left pad array."""
        for pad_array in self.pad_arrays:
            bbox = pad_array.bbox()
            if pad_array.spacing.y and bbox.is_defined() and bbox.center.x < 0:
                return pad_array
        return None

    def _get_bounding_box_of_vertical_pad_arrays(self) -> BoundingBox:
        """Get the bounding box of the vertical pad arrays."""
        bb = BoundingBox()
        for pad_array in self.pad_arrays:
            if pad_array.spacing.y:
                bb.include_bbox(pad_array.bbox())
        return bb

    def _get_bounding_box_of_horizontal_pad_arrays(self) -> BoundingBox:
        """Get the bounding box of the horizontal pad arrays."""
        bb = BoundingBox()
        for pad_array in self.pad_arrays:
            if pad_array.spacing.x:
                bb.include_bbox(pad_array.bbox())
        return bb

    def _create_arrow(self) -> pin1_arrow.Pin1SilkscreenArrow:
        r"""Create a pin-1 arrow for a quad (4-sided) package.

        The arrow is placed at the corner nearest to pin 1 and points toward
        the pad array containing pin 1.

        Pin 1 on left side (standard QFN):

        .. aafig::

              +---+    +---+  +---+
               \ /     |   |  |   |
                + -----|   |--|   |-- ...
                |      +---+  +---+
            +---+-+
            |     |
            +---+-+
                |
                ...
        """
        silk_fab_offset = self.global_config.silk_fab_offset

        body_x_half = self.body_size.x / 2
        body_y_half = self.body_size.y / 2

        top_array = self._get_top_pad_array()
        left_array = self._get_left_pad_array()

        pads_bbox_vert = left_array.bbox() if left_array else BoundingBox()
        pads_bbox_hor = top_array.bbox() if top_array else BoundingBox()

        # Find the pin with the lowest pad number (pin1):
        idx_array, idx_pad = find_lowest_numbered_pad(self.pad_arrays)
        pads = self.pad_arrays[idx_array].children
        pad1 = pads[idx_pad]

        # Determine the quadrant of pin 1
        # Start in north-west (usual)
        silk_corner = Vector2D(
            -body_x_half - silk_fab_offset,
            -body_y_half - silk_fab_offset,
        )

        if pad1.at.x > 0:
            silk_corner.x *= -1
        if pad1.at.y > 0:
            silk_corner.y *= -1

        # Figure out which array contains the pin 1 pad
        # If it's the top array, the arrow points east, otherwise south.
        if top_array is not None and top_array == self.pad_arrays[idx_array]:
            arrow_direction = Direction.EAST
        else:
            arrow_direction = Direction.SOUTH

        arrow_size = SilkArrowSize.MEDIUM

        if self.body_size.min_val <= self.SMALL_ARROW_CUTOFF:
            arrow_size = SilkArrowSize.SMALL

        return draw_silk_triangle_in_corner(
            self.global_config,
            silk_corner,
            arrow_direction,
            arrow_size,
            pads_bbox_hor,
            pads_bbox_vert,
        )

    def _create_silk(self) -> None:
        silk_line_width = self.global_config.silk_line_width
        silk_pad_offset = self.global_config.silk_pad_offset
        silk_fab_offset = self.global_config.silk_fab_offset

        arrow = self._create_arrow()
        self.append(arrow)

        # Draw the component outline on the silk screen:
        #
        #      +----------------+  <- silk
        #      | +------------+ |
        #    =====            ==== <- pad
        #        |            |
        #    =====            ====
        #      | +------------+ |
        #      +----------------+

        # Normal QFN style - silk hugs the nominal body
        silk_box = BoundingBox.by_center_and_size(Vector2D(0, 0), self.body_size)
        silk_box.inflate(silk_fab_offset)

        # Push the silk out only at the ENDs of the arrays.
        # In most cases where the corners don't have pads, this doesn't have any effect,
        # but if there are pads that get very near to the corners, it will allow the
        # silk to not be completely deleted by the pad keepouts.
        # An example of where this kicks in is Analog_LFCSP-UQ-10_1.3x1.6mm_P0.4mm
        #
        # That can also help with pullback/LGA devices which have corner pads, such as
        # Kionix_LGA-12_2x2mm_P0.5mm_LayoutBorder2x4y, but a more intentional solution for
        # them might be a full box outside the pads entirely.

        pads_bbox_vert = self._get_bounding_box_of_vertical_pad_arrays()
        pads_bbox_hor = self._get_bounding_box_of_horizontal_pad_arrays()

        pads_bbox_vert.inflate(silk_pad_offset)
        pads_bbox_hor.inflate(silk_pad_offset)

        if pads_bbox_vert.is_defined():
            silk_box.include_point(pads_bbox_vert.top_midpoint)
            silk_box.include_point(pads_bbox_vert.bottom_midpoint)
        if pads_bbox_hor.is_defined():
            silk_box.include_point(pads_bbox_hor.right_midpoint)
            silk_box.include_point(pads_bbox_hor.left_midpoint)

        # The silk outline might need to be trimmed around the arrow:
        g_silk_kept = subtract(
            GeomRectangle(silk_box),
            arrow.as_polygon(inflation=silk_line_width * 2),
        )

        # Trim the silk outline around the pads:
        keepouts: list[GeomShapesClosed] = []

        for pad_array in self.pad_arrays:
            keepouts.extend(pad_array.as_geom_shapes(inflation=silk_pad_offset))

        if self.exposed_pad is not None:
            keepouts.append(self.exposed_pad.as_geom_shape(inflation=silk_pad_offset))

        g_silk_kept = applyKeepouts(items=g_silk_kept, keepouts=keepouts)

        for shape in g_silk_kept:
            self.append(
                shape_to_node(shape=shape, layer="F.SilkS", width=silk_line_width)
            )
