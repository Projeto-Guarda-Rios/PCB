# kilibs is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# kilibs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with kilibs.
# If not, see < http://www.gnu.org/licenses/ >.
#
# (C) The KiCad Librarian Team

"""Definitions for directions."""

from __future__ import annotations

import enum


class Direction(enum.Enum):
    """An enumeration class associating the cardinal directions to their angle."""

    NORTH = 90
    """Up."""
    EAST = 0
    """Right."""
    SOUTH = 270
    """Down."""
    WEST = 180
    """Left."""
    NORTHEAST = 45
    """Up-right."""
    NORTHWEST = 135
    """Up-left."""
    SOUTHEAST = 315
    """Down-right."""
    SOUTHWEST = 225
    """Down-left."""

    @classmethod
    def nearest_cardinal(cls, angle: float | Direction) -> Direction:
        """
        Return the closest of NSEW from an angle/heading.

        Rounds anticlockwise: 45 is North.
        """

        if isinstance(angle, Direction):
            angle = angle.value

        # Normalise to 0..360
        while angle < 0:
            angle += 360
        while angle > 360:
            angle -= 360

        if angle < 45 or angle >= 315:
            return Direction.EAST
        if angle < 135:
            return Direction.NORTH
        if angle < 225:
            return Direction.WEST

        return Direction.SOUTH

    def is_cardinal(self) -> bool:
        return self in [
            Direction.NORTH,
            Direction.SOUTH,
            Direction.EAST,
            Direction.WEST,
        ]

    def is_diagonal(self) -> bool:
        return self in [
            Direction.NORTHEAST,
            Direction.NORTHWEST,
            Direction.SOUTHEAST,
            Direction.SOUTHWEST,
        ]

    def is_north_south(self) -> bool:
        return self in [
            Direction.NORTH,
            Direction.SOUTH,
        ]

    def is_east_west(self) -> bool:
        return self in [
            Direction.EAST,
            Direction.WEST,
        ]
