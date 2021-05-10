from backend.graph_providers.loading_graph_provider import LoadingGraphProvider
import osmnx

# Build a graph on a random road in Kansas
def build_example_graph():
    origin = (38.815302, -101.049285)
    destination = (38.815235, -101.039543)
    return LoadingGraphProvider(origin, destination)

# Make sure reference point is in graph
def test_check_nodes_exist():
    example_graph = build_example_graph()
    assert 121144825 in example_graph.get_all_nodes()

# Make sure all expected nodes are in the graph
def test_get_all_nodes():
    example_graph = build_example_graph()
    nodes = list(example_graph.get_all_nodes())
    assert len(nodes) == 35

# Test a node's known neighbors (none outside of box, as loading would)
def test_get_neighbors():
    example_graph = build_example_graph()
    neighbors = list(example_graph.get_neighbors(121144825))
    assert neighbors == [121144827, 121144823]

# Check distance between two nodes
def test_get_edge_distance_and_estimate():
    example_graph = build_example_graph()
    # Estimated distance (coordinate values)
    assert example_graph.get_distance_estimate(121144808, 121144810) == 0.02500729703504296
    # Actual road distance (meters)
    assert example_graph.get_edge_distance(121144808, 121144810) == 55.214

# Ensure node coordinates don't change between versions
def test_get_coords():
    example_graph = build_example_graph()
    coordinates = example_graph.get_coords(121144825)
    assert coordinates['x'] == -101.029813
    assert coordinates['y'] == 38.800627
    assert coordinates['z'] == 885.233

def test_lazy_loading():
    example_graph = build_example_graph()
    nodes_loaded_before = len(example_graph.get_all_nodes())
    example_graph.get_neighbors(121130123)
    nodes_loaded_after = len(example_graph.get_all_nodes())
    assert nodes_loaded_after > nodes_loaded_before