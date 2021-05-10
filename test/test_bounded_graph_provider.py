from backend.graph_providers.bounded_graph_provider import BoundedGraphProvider
import osmnx

"""
The tests in this file will use a real world example.
Note that this could possibly fail due to OpenStreetMap changes.
That's intended, as bounded_graph_provider is an interface between us and OSM.
If OSM changes, so must bounded_graph_provider.
"""

# Build a graph on a random road in Kansas
def build_example_graph():
    origin = (38.815302, -101.049285)
    destination = (38.815235, -101.039543)
    return BoundedGraphProvider(origin, destination)

# Make sure reference point is in graph
def test_check_nodes_exist():
    example_graph = build_example_graph()
    assert 121130127 in example_graph.graph.nodes

# Make sure all expected nodes are in the graph
def test_get_all_nodes():
    example_graph = build_example_graph()
    nodes = list(example_graph.get_all_nodes())
    assert nodes == [121130127, 121130132, 121130135, 121130136]

# Test a node's known neighbors (none outside of box, as loading would)
def test_get_neighbors():
    example_graph = build_example_graph()
    neighbors = list(example_graph.get_neighbors(121130127))
    assert neighbors == [121130132]

# Check distance between two nodes
def test_get_edge_distance_and_estimate():
    example_graph = build_example_graph()
    # Estimated distance (coordinate values)
    assert example_graph.get_distance_estimate(121130127, 121130132) == 1.9080002657573345
    # Actual road distance (meters)
    assert example_graph.get_edge_distance(121130127, 121130132) == 87.252

# Ensure node coordinates don't change between versions
def test_get_coords():
    example_graph = build_example_graph()
    coordinates = example_graph.get_coords(121130127)
    assert coordinates['x'] == -101.038297
    assert coordinates['y'] == 38.815313
    assert coordinates['z'] == 895.292
