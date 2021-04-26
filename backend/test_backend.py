import pytest
from aStarSearch import *
from bounded_graph_provider import *
from currObj import *
from dijkstra import *
from dummy_route import *
from loading_graph_provider import *
from router import *
# from timeout import *

class TestBackend:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")