import copy
from collections import deque
from typing import Any, Dict, List, Union

from bisheng.interface.utils import extract_input_variables_from_prompt


class UnbuiltObject:
    pass


def validate_prompt(prompt: str):
    """Validate prompt."""
    if extract_input_variables_from_prompt(prompt):
        return prompt

    return fix_prompt(prompt)


def fix_prompt(prompt: str):
    """Fix prompt."""
    return prompt + ' {input}'


def flatten_list(list_of_lists: list[Union[list, Any]]) -> list:
    """Flatten list of lists."""
    new_list = []
    for item in list_of_lists:
        if isinstance(item, list):
            new_list.extend(item)
        else:
            new_list.append(item)
    return new_list


def find_last_node(nodes, edges):
    """
    This function receives a flow and returns the last node.
    """
    return next((n for n in nodes if all(e['source'] != n['id'] for e in edges)), None)


def add_parent_node_id(nodes, parent_node_id):
    """
    This function receives a list of nodes and adds a parent_node_id to each node.
    """
    for node in nodes:
        node['parent_node_id'] = parent_node_id


def ungroup_node(group_node_data, base_flow):
    template, flow = (
        group_node_data['node']['template'],
        group_node_data['node']['flow'],
    )
    parent_node_id = group_node_data['id']
    g_nodes = flow['data']['nodes']
    add_parent_node_id(g_nodes, parent_node_id)
    g_edges = flow['data']['edges']

    # Redirect edges to the correct proxy node
    updated_edges = get_updated_edges(base_flow, g_nodes, g_edges, group_node_data['id'])

    # Update template values
    update_template(template, g_nodes)

    nodes = [n for n in base_flow['nodes'] if n['id'] != group_node_data['id']] + g_nodes
    edges = ([
        e for e in base_flow['edges']
        if e['target'] != group_node_data['id'] and e['source'] != group_node_data['id']
    ] + g_edges + updated_edges)

    base_flow['nodes'] = nodes
    base_flow['edges'] = edges

    return nodes


def raw_topological_sort(nodes, edges) -> List[Dict]:
    # Redefine the above function but using the nodes and self._edges
    # which are dicts instead of Vertex and Edge objects
    # nodes have an id, edges have a source and target keys
    # return a list of node ids in topological order

    # States: 0 = unvisited, 1 = visiting, 2 = visited
    state = {node['id']: 0 for node in nodes}
    nodes_dict = {node['id']: node for node in nodes}
    sorted_vertices = []

    def dfs(node):
        if state[node] == 1:
            # We have a cycle
            raise ValueError('Graph contains a cycle, cannot perform topological sort')
        if state[node] == 0:
            state[node] = 1
            for edge in edges:
                if edge['source'] == node:
                    dfs(edge['target'])
            state[node] = 2
            sorted_vertices.append(node)

    # Visit each node
    for node in nodes:
        if state[node['id']] == 0:
            dfs(node['id'])

    reverse_sorted = list(reversed(sorted_vertices))
    return [nodes_dict[node_id] for node_id in reverse_sorted]


def process_flow(flow_object):
    cloned_flow = copy.deepcopy(flow_object)
    processed_nodes = set()  # To keep track of processed nodes

    def process_node(node):
        node_id = node.get('id')

        # If node already processed, skip
        if node_id in processed_nodes:
            return

        if node.get('data') and node['data'].get('node') and node['data']['node'].get('flow'):
            process_flow(node['data']['node']['flow']['data'])
            new_nodes = ungroup_node(node['data'], cloned_flow)
            # Add new nodes to the queue for future processing
            nodes_to_process.extend(new_nodes)

        # Mark node as processed
        processed_nodes.add(node_id)

    sorted_nodes_list = raw_topological_sort(cloned_flow['nodes'], cloned_flow['edges'])
    nodes_to_process = deque(sorted_nodes_list)

    while nodes_to_process:
        node = nodes_to_process.popleft()
        process_node(node)

    return cloned_flow


def update_template(template, g_nodes):
    """
    Updates the template of a node in a graph with the given template.

    Args:
        template (dict): The new template to update the node with.
        g_nodes (list): The list of nodes in the graph.

    Returns:
        None
    """
    for _, value in template.items():
        if not value.get('proxy'):
            continue
        proxy_dict = value['proxy']
        field, id_ = proxy_dict['field'], proxy_dict['id']
        node_index = next((i for i, n in enumerate(g_nodes) if n['id'] == id_), -1)
        if node_index != -1:
            display_name = None
            show = g_nodes[node_index]['data']['node']['template'][field].get('show', False)
            advanced = g_nodes[node_index]['data']['node']['template'][field]['advanced']
            if 'display_name' in g_nodes[node_index]['data']['node']['template'][field]:
                display_name = g_nodes[node_index]['data']['node']['template'][field][
                    'display_name']
            else:
                display_name = g_nodes[node_index]['data']['node']['template'][field]['name']

            g_nodes[node_index]['data']['node']['template'][field] = value
            g_nodes[node_index]['data']['node']['template'][field]['show'] = show
            g_nodes[node_index]['data']['node']['template'][field]['advanced'] = advanced
            g_nodes[node_index]['data']['node']['template'][field]['display_name'] = display_name


def update_target_handle(
    new_edge,
    g_nodes,
    group_node_id,
):
    """
    Updates the target handle of a given edge if it is a proxy node.

    Args:
        new_edge (dict): The edge to update.
        g_nodes (list): The list of nodes in the graph.
        group_node_id (str): The ID of the group node.

    Returns:
        dict: The updated edge.
    """
    # 兼容逻辑
    for node in g_nodes:
        if node['id'] in new_edge['targetHandle']:
            new_edge['target'] = node['id']
            break
    return new_edge


def set_new_target_handle(proxy_id, new_edge, target_handle, node):
    """
    Sets a new target handle for a given edge.

    Args:
        proxy_id (str): The ID of the proxy.
        new_edge (dict): The new edge to be created.
        target_handle (dict): The target handle of the edge.
        node (dict): The node containing the edge.

    Returns:
        None
    """
    new_edge['target'] = proxy_id
    _type = target_handle.get('type')
    if _type is None:
        raise KeyError("The 'type' key must be present in target_handle.")

    field = target_handle['proxy']['field']
    new_target_handle = {
        'fieldName': field,
        'type': _type,
        'id': proxy_id,
    }
    if node['data']['node'].get('flow'):
        new_target_handle['proxy'] = {
            'field': node['data']['node']['template'][field]['proxy']['field'],
            'id': node['data']['node']['template'][field]['proxy']['id'],
        }
    if input_types := target_handle.get('inputTypes'):
        new_target_handle['inputTypes'] = input_types
    if not new_edge.get('data'):
        new_edge['data'] = {}
    new_edge['data']['targetHandle'] = new_target_handle


def update_source_handle(new_edge, g_nodes, g_edges):
    """
    Updates the source handle of a given edge to the last node in the flow data.

    Args:
        new_edge (dict): The edge to update.
        flow_data (dict): The flow data containing the nodes and edges.

    Returns:
        dict: The updated edge with the new source handle.
    """
    last_node = copy.deepcopy(find_last_node(g_nodes, g_edges))
    new_edge['sourceHandle'] = new_edge['sourceHandle'].replace(new_edge['source'],
                                                                last_node['id'])
    new_edge['source'] = last_node['id']
    return new_edge


def get_updated_edges(base_flow, g_nodes, g_edges, group_node_id):
    """
    Given a base flow, a list of graph nodes and a group node id, returns a list of updated edges.
    An updated edge is an edge that has its target or source handle updated based on the group node id.

    Args:
        base_flow (dict): The base flow containing a list of edges.
        g_nodes (list): A list of graph nodes.
        group_node_id (str): The id of the group node.

    Returns:
        list: A list of updated edges.
    """
    updated_edges = []
    for edge in base_flow['edges']:
        new_edge = copy.deepcopy(edge)
        if new_edge['target'] == group_node_id:
            new_edge = update_target_handle(new_edge, g_nodes, group_node_id)

        if new_edge['source'] == group_node_id:
            new_edge = update_source_handle(new_edge, g_nodes, g_edges)

        if edge['target'] == group_node_id or edge['source'] == group_node_id:
            updated_edges.append(new_edge)
    return updated_edges


def find_next_node(graph_data: Dict, node_id: str) -> List[Dict]:
    """
    Finds the next node in the graph data based on the given node id.
    """
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])

    edges_ = [e['target'] for e in edges if e['source'] == node_id]
    return [n for n in nodes if n['id'] in edges_]


def cut_graph_bynode(graph_data: Dict, node_id: str) -> List[Dict]:
    """
    通过node_id 找到和node相关的所有依赖节点。
    """
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])

    nodes_new_list = []
    edges_new_list = []
    iflast = True
    for e in edges:
        if e['target'] == node_id:
            iflast = False
            node_list, edge_list = cut_graph_bynode(graph_data, e['source'])
            nodes_new_list.extend(node_list)
            edges_new_list.extend(edge_list)
            nodes_new_list.append([n for n in nodes if n['id'] == node_id][0])
            edges_new_list.append(e)
    if iflast:
        for node in nodes:
            if node['id'] == node_id:
                return [node], []

    return nodes_new_list, edges_new_list
