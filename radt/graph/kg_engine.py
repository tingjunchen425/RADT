import networkx as nx
import json
from typing import List, Dict, Any, Optional

class ActiveKG:
    """
    RADT 2.0 Active Knowledge Graph (Graph RAG Engine)
    Uses NetworkX for managing the Hub-and-Spoke RAG structure.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any] = None):
        """Add a node to the active knowledge graph."""
        props = properties or {}
        self.graph.add_node(node_id, type=node_type, **props)
        
    def add_edge(self, source_id: str, target_id: str, relation_type: str, properties: Dict[str, Any] = None):
        """Add a directed edge representing a relationship."""
        props = properties or {}
        self.graph.add_edge(source_id, target_id, relation=relation_type, **props)
        
    def update_node_state(self, node_id: str, updates: Dict[str, Any]):
        """Update properties of an existing node (e.g. status, gathered info)."""
        if self.graph.has_node(node_id):
            for k, v in updates.items():
                self.graph.nodes[node_id][k] = v
                
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self.graph.has_node(node_id):
            return self.graph.nodes[node_id]
        return None

    def get_sub_nodes(self, parent_id: str, relation_type: str = None) -> List[str]:
        """Get all child nodes of a specific parent, optionally filtered by relation type."""
        sub_nodes = []
        if self.graph.has_node(parent_id):
            for neighbor in self.graph.successors(parent_id):
                if relation_type is None or self.graph.edges[parent_id, neighbor].get('relation') == relation_type:
                    sub_nodes.append(neighbor)
        return sub_nodes

    def extract_rag_context(self, target_node: str) -> str:
        """Extract surrounding subgraph context for Graph RAG purposes."""
        if not self.graph.has_node(target_node):
            return "No context found."
            
        context = []
        node_data = self.graph.nodes[target_node]
        context.append(f"Target [{target_node}] ({node_data.get('type', 'Unknown')}): {json.dumps(node_data)}")
        
        for neighbor in self.graph.successors(target_node):
            edge_data = self.graph.edges[target_node, neighbor]
            neighbor_data = self.graph.nodes[neighbor]
            context.append(f"  -> {edge_data.get('relation', 'related_to')} -> [{neighbor}] ({neighbor_data.get('type', 'Unknown')}): {json.dumps(neighbor_data)}")
            
        for prep in self.graph.predecessors(target_node):
            edge_data = self.graph.edges[prep, target_node]
            prep_data = self.graph.nodes[prep]
            context.append(f"  <- {edge_data.get('relation', 'related_to')} <- [{prep}] ({prep_data.get('type', 'Unknown')}): {json.dumps(prep_data)}")
            
        return "\n".join(context)

    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary for persistence or inspection."""
        return nx.node_link_data(self.graph)
