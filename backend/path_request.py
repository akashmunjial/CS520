class PathRequest:
    """Parses and stores path settings received from front end.
    """
    def __init__(self, origin, destination, distance_percent, ele_setting, graph_setting):
        self.origin = origin
        self.destination = destination
        self.distance_percent = distance_percent
        self.ele_setting = ele_setting
        self.graph_setting = graph_setting

    def string_to_tuple(self, string):
        """Takes a string in the form of a 2-tuple of floats, returns tuple.

        Args:
            string: A string of form '(<float>, <float>)'

        Returns:
            A tuple obtained by parsing the string.

        Raises:
            A ValueError if 'string' is not in the proper format.
        """
        try:
            translated = tuple(float(x) for x in string[1:-1].split(', '))
        except ValueError:
            raise ValueError("'string' must be of the form '(<float>, <float>)'") from None
        return translated

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, origin):
        if not isinstance(origin, str):
            raise ValueError("'origin' must be a string")
        origin_tuple = self.string_to_tuple(origin)
        self._origin = origin_tuple

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, destination):
        if not isinstance(destination, str):
            raise ValueError("'destination' must be a string")
        destination_tuple = self.string_to_tuple(destination)
        self._destination = destination_tuple

    @property
    def distance_percent(self):
        return self._distance_percent

    @distance_percent.setter
    def distance_percent(self, distance_percent):
        if not isinstance(distance_percent, str):
            raise ValueError("'distance_percent' must be a string")
        try:
            distance_percent = int(distance_percent)
        except ValueError:
            raise ValueError("'distance_percent' must be interpretable as an int") from None
        if distance_percent < 100.:
            raise ValueError("'distance percent' must be no less than 100")
        self._distance_percent = distance_percent

    @property
    def ele_setting(self):
        return self._ele_setting

    @ele_setting.setter
    def ele_setting(self, ele_setting):
        if not isinstance(ele_setting, str):
            raise ValueError("'ele_setting' must be a string")
        possible_ele_settings = ['maximal', 'minimal', 'shortest']
        if ele_setting in possible_ele_settings:
            self._ele_setting = ele_setting
        else:
            raise ValueError(f"'ele_setting' was not among {possible_ele_settings}") from None

    @property
    def graph_setting(self):
        return self._graph_setting

    @graph_setting.setter
    def graph_setting(self, graph_setting):
        if not isinstance(graph_setting, str):
            raise ValueError("'graph_setting' must be a string")
        possible_graph_settings = ['bounded', 'loading']
        if graph_setting in possible_graph_settings:
            self._graph_setting = graph_setting
        else:
            raise ValueError(f"'graph_setting' was not among {possible_graph_settings}") from None
