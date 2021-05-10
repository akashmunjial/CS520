import pytest
from collections import namedtuple

from backend.path_request import PathRequest


values = namedtuple('Values', ['o', 'd', 'dp', 'es', 'gs'])

def get_good_values():
    # Some inputs that should be accepted by PathRequest
    origin = '(3.3, 2.2)'
    destination = '(3.3, 2.2)'
    distance_percent = '120'
    ele_setting = 'minimal'
    graph_setting = 'loading'

    return values(origin, destination, distance_percent, ele_setting, graph_setting)


def test_input_validation_must_be_strings():
    # Good inputs
    good = get_good_values()

    # Should pass without expcetion
    req = PathRequest(good.o, good.d, good.dp, good.es, good.gs)

    # All inputs must be strings, so should get errors here
    with pytest.raises(ValueError):
        req = PathRequest((3.3, 2.2), good.d, good.dp, good.es, good.gs)
    with pytest.raises(ValueError):
        req = PathRequest(good.o, (3.3, 2.2), good.dp, good.es, good.gs)
    with pytest.raises(ValueError):
        req = PathRequest(good.o, good.d, 120, good.es, good.gs)
    with pytest.raises(ValueError):
        req = PathRequest(good.o, good.d, good.dp, 1, good.gs)
    with pytest.raises(ValueError):
        req = PathRequest(good.o, good.d, good.dp, good.es, 1)


def test_input_validation_distance_percent():
    # Good inputs
    good = get_good_values()

    # Test that we check it can be parsed as int
    with pytest.raises(ValueError):
        req = PathRequest(good.o, good.d, '2.2', good.es, good.gs)
    # Test that we check range correctly
    with pytest.raises(ValueError):
        req = PathRequest(good.o, good.d, '99', good.es, good.gs)


def test_input_validation_settings():
    # Good inputs
    good = get_good_values()

    # Test that we check elevation setting against valid choices
    with pytest.raises(ValueError):
        req = PathRequest(good.o, good.d, good.dp, 'filler', good.gs)
    # Test that we check graph setting against valid choices
    with pytest.raises(ValueError):
        req = PathRequest(good.o, good.d, good.dp, good.es, 'filler')

