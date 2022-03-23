import typing
import dataclasses
import re

import railostools.exceptions as ros_exc


@dataclasses.dataclass
class Coordinate:
    X: int
    Y: int

    def __getitem__(self, index) -> typing.Tuple[int, int]:
        if index < 0 or index > 1:
            raise ValueError("Index must be 0, 1")
        return self.X if index == 0 else self.Y

    def __str__(self) -> str:
        _sign_x = "N" if self.X < 0 else ""
        _sign_y = "N" if self.Y < 0 else ""
        return f"{_sign_x}{abs(self.X)}-{_sign_y}{abs(self.Y)}"

    def to_dict(self) -> str:
        return self.__str__()

    def __abs__(self) -> int:
        return int(pow(self.X**2+self.Y**2, 0.5))

    def __sub__(self, other):
        return Coordinate(self.X-other.X, self.Y-other.Y)

    def __add__(self, other):
        return Coordinate(self.X+other.X, self.Y+other.Y)


def coord_from_str(coordinate_str: str) -> Coordinate:
    """Convert an ROS coordinate string to a coordinate object"""
    _coord_regex = re.compile(r"^N*\d+\-N*\d+$")

    if not _coord_regex.findall(coordinate_str):
        raise ros_exc.ParsingError(
            f"Invalid coordinate '{coordinate_str}'"
        )

    _coord = coordinate_str.split("-")
    return Coordinate(*(int(i.replace("N", "-")) for i in _coord))