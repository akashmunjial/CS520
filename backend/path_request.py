class PathRequest:
    def __init__(self, origin, destination, distance_percent, ele_setting, graph_setting):
        # Translate geodata for osmnx '(lat, lng)' -> (lat, lng)
        try:
            self.start_coords = tuple(float(x) for x in origin[1:-1].split(', '))
            self.end_coords = tuple(float(x) for x in destination[1:-1].split(', '))
        except ValueError:
            raise ValueError("'origin' and 'destination' must be of the form '(<float>, <float>)'") from None

        try:
            self.distance_percent = int(distance_percent)
        except ValueError:
            raise ValueError("'distance_percent' must be interpretable as an int") from None

        possible_ele_settings = ['maximal', 'minimal', 'shortest']
        if ele_setting in possible_ele_settings:
            self.ele_setting = ele_setting
        else:
            raise ValueError(f"'ele_setting' was not among {possible_ele_settings}") from None

        possible_graph_settings = ['bounded', 'loading']
        if graph_setting in possible_graph_settings:
            self.graph_setting = graph_setting
        else:
            raise ValueError(f"'graph_setting' was not among {possible_graph_settings}") from None
