import datetime
import logging
import os.path

from typing import Any, Dict, List

from rostools.exceptions import RailwayParsingError


class RlyParser:
    _logger = logging.getLogger('ROSTools.RlyParser')

    def __init__(self) -> None:
        self._logger.debug('Creating new RlyParser')
        self._rly_data = {}
        self._start_time: datetime.datetime = None
        self._current_file = None

    def parse(self, rly_file: str) -> None:
        self._logger.info(f"Parsing RLY file '{rly_file}'")
        if not os.path.exists(rly_file):
            raise FileNotFoundError(
                f"Cannot parse railway file '{rly_file}', "
                "file does not exist."
            )
        self._rly_data[rly_file] = self._get_rly_components(open(rly_file).read())
        self._current_file = rly_file

    @property
    def n_active_elements(self) -> int:
        if not self._current_file:
            raise RailwayParsingError("No file has been parsed yet")
        return self._rly_data[self._current_file]['n_active_elements']

    @property
    def n_inactive_elements(self) -> int:
        if not self._current_file:
            raise RailwayParsingError("No file has been parsed yet")
        return self._rly_data[self._current_file]['n_inactive_elements']

    @property
    def program_version(self) -> str:
        if not self._current_file:
            raise RailwayParsingError("No file has been parsed yet")
        return self._rly_data[self._current_file]['program_version']

    def _parse_map(self, component_data: List[str]):
        _map_dict = {'active_elements': [], 'inactive_elements': []}

        _n_inactive = 0
        _end = 0

        for i in range(0, len(component_data), 3):
            if 'Inactive elements' in component_data[i][2]:
                _n_inactive = int(component_data[i][1])
                _end = i
                break
            _speed_tag = int(component_data[i][1])

            _position = (int(component_data[i][2]), int(component_data[i][3]))

            _length = (
                int(component_data[i][4]),
                int(component_data[i][5])
                if component_data[i][5] != '-1' else None
            )

            _speed_limits = (
                int(component_data[i][6]),
                int(component_data[i][7])
                if component_data[i][7] != '-1' else None
            )

            _map_dict['active_elements'].append({
                'speed_tag': _speed_tag,
                'position': _position,
                'length': _length,
                'speed_limit': _speed_limits,
                'location_name': component_data[i+1][1] if component_data[i+1][1] else None,
                'active_element_name': component_data[i+2][0] if component_data[i+2][0] else None
            })

        for i in range(_end + 1, len(component_data), 3):
            if '****' in component_data[i][1]:
                break
            _speed_tag = int(component_data[i][1])
            _position = (int(component_data[i][2]), int(component_data[i][3]))

            _map_dict['inactive_elements'].append({
                'speed_tag': _speed_tag,
                'position': _position,
                'location_name': component_data[i + 1][0] if component_data[i + 1][0] else None,
            })

        return {'elements': _map_dict, 'n_inactive_elements': _n_inactive}

    def _get_rly_components(self, railway_file_data: str) -> Dict[str, Any]:
        self._logger.debug('Retrieving components from extracted railway file data')
        _rly_components: List[str] = railway_file_data.split('\0')
        _rly_components = [i.split('\n') for i in _rly_components]

        _program_version = _rly_components[0][0]
        _home_position = (int(_rly_components[1][1]), int(_rly_components[1][2]))
        _n_elements = _rly_components[1][3]
        _data_dict = {
            'program_version': _program_version,
            'home_position': _home_position,
            'n_active_elements': _n_elements,
            'user_graphics': _rly_components[1][4][-1] == '1'
        }
        _data_dict.update(self._parse_map(_rly_components[2:]))
        return _data_dict
