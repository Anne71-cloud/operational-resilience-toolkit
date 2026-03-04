"""
Dependency Mapper — Critical Function & Dependency Mapping Engine

Maps critical business functions to their end-to-end dependencies across technology,
people, processes, third parties, and data. Uses graph-based analysis to identify
single points of failure, concentration risks, and critical chains.

Regulatory alignment:
- DORA Art. 8-9: ICT risk management framework & identification
- FINMA Cm 31-40: Identification of critical functions and dependencies
- PRA SS1/21 5.1-5.6: Mapping of important business services
- BCBS 516 P3-P4: Critical operations and interdependencies
"""

import networkx as nx
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import json


@dataclass
class CriticalFunction:
    """Represents a critical business function / important business service."""
    name: str
    tier: int  # 1 = most critical, 3 = least critical
    owner: str = ""
    description: str = ""
    regulatory_classification: str = ""  # e.g., "DORA Critical", "FINMA Essential"
    max_acceptable_downtime_hours: float = 0.0
    revenue_at_risk: float = 0.0
    customers_impacted: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Dependency:
    """Represents a dependency (technology, third-party, people, process, data)."""
    name: str
    dep_type: str  # technology, third_party, people, process, data, infrastructure
    provider: str = ""
    criticality: str = "medium"  # critical, high, medium, low
    substitutability: str = "medium"  # none, low, medium, high
    recovery_time_hours: float = 0.0
    geographic_location: str = ""
    contract_end_date: str = ""


class DependencyMapper:
    """
    Graph-based dependency mapping engine for operational resilience.
    
    Uses directed graphs to model relationships between critical functions
    and their dependencies, enabling analysis of failure propagation paths,
    single points of failure, and concentration risks.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.critical_functions: dict[str, CriticalFunction] = {}
        self.dependencies: dict[str, Dependency] = {}
    
    def add_critical_function(self, name: str, tier: int = 1, **kwargs) -> CriticalFunction:
        """Register a critical business function."""
        cf = CriticalFunction(name=name, tier=tier, **kwargs)
        self.critical_functions[name] = cf
        self.graph.add_node(name, node_type="critical_function", tier=tier, **kwargs)
        return cf
    
    def add_dependency(self, function_name: str, dependency_name: str,
                       dep_type: str = "technology", **kwargs) -> Dependency:
        """Add a dependency to a critical function."""
        dep = Dependency(name=dependency_name, dep_type=dep_type, **kwargs)
        self.dependencies[dependency_name] = dep
        
        if dependency_name not in self.graph:
            self.graph.add_node(dependency_name, node_type="dependency",
                              dep_type=dep_type, **kwargs)
        
        self.graph.add_edge(function_name, dependency_name,
                           dep_type=dep_type, **kwargs)
        return dep
    
    def add_sub_dependency(self, parent_dep: str, child_dep: str,
                           dep_type: str = "technology", **kwargs):
        """Add a dependency chain (dependency depends on another dependency)."""
        if child_dep not in self.graph:
            self.graph.add_node(child_dep, node_type="dependency",
                              dep_type=dep_type, **kwargs)
        self.graph.add_edge(parent_dep, child_dep, dep_type=dep_type, **kwargs)
    
    def find_single_points_of_failure(self) -> list[dict]:
        """
        Identify single points of failure — dependencies that, if they fail,
        would disrupt one or more critical functions with no alternative path.
        
        A SPOF is a node whose removal disconnects a critical function from
        one or more of its essential dependencies.
        """
        spofs = []
        
        for dep_name, dep_data in self.graph.nodes(data=True):
            if dep_data.get("node_type") != "dependency":
                continue
            
            # Find all critical functions that depend on this node
            impacted_functions = []
            for cf_name in self.critical_functions:
                if self.graph.has_node(cf_name) and nx.has_path(self.graph, cf_name, dep_name):
                    # Check if there's only one path
                    paths = list(nx.all_simple_paths(self.graph, cf_name, dep_name))
                    if len(paths) == 1:
                        impacted_functions.append(cf_name)
            
            if impacted_functions:
                spofs.append({
                    "dependency": dep_name,
                    "type": dep_data.get("dep_type", "unknown"),
                    "impacted_functions": impacted_functions,
                    "impact_count": len(impacted_functions),
                    "risk_level": "critical" if len(impacted_functions) >= 2 else "high"
                })
        
        return sorted(spofs, key=lambda x: x["impact_count"], reverse=True)
    
    def find_concentration_risks(self, threshold: int = 2) -> list[dict]:
        """
        Identify concentration risks — single providers or systems that
        multiple critical functions depend on.
        
        Args:
            threshold: Minimum number of dependent functions to flag as concentration risk
        """
        concentration = []
        
        for node in self.graph.nodes():
            predecessors = list(self.graph.predecessors(node))
            dependent_cfs = [p for p in predecessors if p in self.critical_functions]
            
            # Also check indirect dependencies
            for cf_name in self.critical_functions:
                if cf_name not in dependent_cfs and self.graph.has_node(cf_name):
                    if nx.has_path(self.graph, cf_name, node):
                        dependent_cfs.append(cf_name)
            
            dependent_cfs = list(set(dependent_cfs))
            
            if len(dependent_cfs) >= threshold:
                concentration.append({
                    "dependency": node,
                    "type": self.graph.nodes[node].get("dep_type", "unknown"),
                    "dependent_functions": dependent_cfs,
                    "concentration_count": len(dependent_cfs),
                    "risk_level": "critical" if len(dependent_cfs) >= 3 else "high"
                })
        
        return sorted(concentration, key=lambda x: x["concentration_count"], reverse=True)
    
    def get_critical_chains(self, function_name: str) -> list[list[str]]:
        """
        Get all dependency chains from a critical function to its leaf dependencies.
        Useful for end-to-end mapping required by DORA Art. 8.
        """
        chains = []
        leaf_nodes = [n for n in self.graph.nodes()
                     if self.graph.out_degree(n) == 0]
        
        for leaf in leaf_nodes:
            if nx.has_path(self.graph, function_name, leaf):
                for path in nx.all_simple_paths(self.graph, function_name, leaf):
                    chains.append(path)
        
        return chains
    
    def get_impact_radius(self, failed_node: str) -> dict:
        """
        Calculate the blast radius if a specific dependency fails.
        Returns all critical functions and dependencies affected.
        """
        affected_functions = []
        affected_dependencies = []
        
        # Find all ancestors (nodes that depend on the failed node)
        ancestors = nx.ancestors(self.graph, failed_node)
        
        for ancestor in ancestors:
            if ancestor in self.critical_functions:
                affected_functions.append(ancestor)
            else:
                affected_dependencies.append(ancestor)
        
        # Find all descendants (nodes the failed node depends on — also impacted)
        descendants = list(nx.descendants(self.graph, failed_node))
        
        return {
            "failed_node": failed_node,
            "affected_critical_functions": affected_functions,
            "affected_dependencies": affected_dependencies,
            "downstream_cascade": descendants,
            "total_impact_radius": len(ancestors) + len(descendants),
        }
    
    def generate_summary_report(self) -> dict:
        """Generate a comprehensive dependency mapping summary."""
        spofs = self.find_single_points_of_failure()
        concentrations = self.find_concentration_risks()
        
        dep_type_counts = {}
        for _, data in self.graph.nodes(data=True):
            dt = data.get("dep_type", "critical_function")
            dep_type_counts[dt] = dep_type_counts.get(dt, 0) + 1
        
        return {
            "total_critical_functions": len(self.critical_functions),
            "total_dependencies": len(self.dependencies),
            "total_connections": self.graph.number_of_edges(),
            "dependency_type_distribution": dep_type_counts,
            "single_points_of_failure": len(spofs),
            "spof_details": spofs[:5],  # Top 5
            "concentration_risks": len(concentrations),
            "concentration_details": concentrations[:5],  # Top 5
            "avg_dependencies_per_function": (
                self.graph.number_of_edges() / max(len(self.critical_functions), 1)
            ),
            "max_chain_depth": max(
                (len(p) for cf in self.critical_functions
                 for p in self.get_critical_chains(cf)),
                default=0
            ),
        }
    
    def export_to_json(self, filepath: str):
        """Export the dependency map to JSON for reporting or integration."""
        data = {
            "critical_functions": {
                name: {
                    "tier": cf.tier,
                    "owner": cf.owner,
                    "description": cf.description,
                    "max_acceptable_downtime_hours": cf.max_acceptable_downtime_hours,
                }
                for name, cf in self.critical_functions.items()
            },
            "dependencies": {
                name: {
                    "type": dep.dep_type,
                    "provider": dep.provider,
                    "criticality": dep.criticality,
                    "substitutability": dep.substitutability,
                    "recovery_time_hours": dep.recovery_time_hours,
                }
                for name, dep in self.dependencies.items()
            },
            "edges": [
                {"from": u, "to": v, **d}
                for u, v, d in self.graph.edges(data=True)
            ],
            "analysis": self.generate_summary_report(),
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        return data
