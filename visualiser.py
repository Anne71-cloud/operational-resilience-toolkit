"""
Dependency Visualiser — Network visualisation for dependency maps.

Creates visual representations of critical function dependency graphs
with risk heat-mapping, colour-coded dependency types, and SPOF highlighting.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from .mapper import DependencyMapper


# Colour scheme for dependency types
DEP_COLOURS = {
    "critical_function": "#1B2A4A",
    "technology": "#2E86AB",
    "third_party": "#E8630A",
    "people": "#7B2D8E",
    "process": "#2D8E6B",
    "data": "#D4A843",
    "infrastructure": "#C23B22",
}

DEP_SHAPES = {
    "critical_function": "s",  # square
    "technology": "o",         # circle
    "third_party": "D",        # diamond
    "people": "^",             # triangle up
    "process": "h",            # hexagon
    "data": "p",               # pentagon
    "infrastructure": "v",     # triangle down
}


def visualise_dependency_map(mapper: DependencyMapper, title: str = "Operational Resilience — Dependency Map",
                              highlight_spofs: bool = True, figsize: tuple = (16, 10),
                              save_path: str = None):
    """
    Create a comprehensive dependency map visualisation.
    
    Args:
        mapper: DependencyMapper instance with populated graph
        title: Chart title
        highlight_spofs: Whether to highlight single points of failure
        figsize: Figure dimensions
        save_path: Optional file path to save the figure
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    G = mapper.graph
    
    if len(G.nodes()) == 0:
        ax.text(0.5, 0.5, "No dependencies mapped yet", ha="center", va="center",
                fontsize=14, color="#666")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        return fig
    
    # Layout
    pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)
    
    # Identify SPOFs for highlighting
    spof_nodes = set()
    if highlight_spofs:
        spofs = mapper.find_single_points_of_failure()
        spof_nodes = {s["dependency"] for s in spofs}
    
    # Draw edges with colour based on dependency type
    for u, v, data in G.edges(data=True):
        dep_type = data.get("dep_type", "technology")
        colour = DEP_COLOURS.get(dep_type, "#999999")
        style = "dashed" if dep_type == "third_party" else "solid"
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=colour,
                              style=style, alpha=0.6, arrows=True,
                              arrowsize=15, ax=ax, width=1.5)
    
    # Draw nodes by type
    for node, data in G.nodes(data=True):
        node_type = data.get("node_type", "dependency")
        dep_type = data.get("dep_type", node_type)
        colour = DEP_COLOURS.get(dep_type, "#999999")
        size = 800 if node_type == "critical_function" else 400
        
        # Highlight SPOFs with red border
        edgecolors = "#FF0000" if node in spof_nodes else colour
        linewidths = 3 if node in spof_nodes else 1.5
        
        nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=colour,
                              node_size=size, alpha=0.85, edgecolors=edgecolors,
                              linewidths=linewidths, ax=ax)
    
    # Labels
    labels = {}
    for node in G.nodes():
        # Truncate long names
        label = node if len(node) <= 20 else node[:18] + "..."
        labels[node] = label
    
    nx.draw_networkx_labels(G, pos, labels, font_size=7, font_weight="bold",
                           font_color="white", ax=ax)
    
    # Legend
    legend_patches = [
        mpatches.Patch(color=DEP_COLOURS["critical_function"], label="Critical Function"),
        mpatches.Patch(color=DEP_COLOURS["technology"], label="Technology"),
        mpatches.Patch(color=DEP_COLOURS["third_party"], label="Third Party"),
        mpatches.Patch(color=DEP_COLOURS["people"], label="People"),
        mpatches.Patch(color=DEP_COLOURS["process"], label="Process"),
        mpatches.Patch(color=DEP_COLOURS["infrastructure"], label="Infrastructure"),
    ]
    if highlight_spofs and spof_nodes:
        legend_patches.append(mpatches.Patch(edgecolor="#FF0000", facecolor="none",
                                              linewidth=2, label="Single Point of Failure"))
    
    ax.legend(handles=legend_patches, loc="upper left", fontsize=8,
             framealpha=0.9, edgecolor="#ccc")
    
    ax.set_title(title, fontsize=14, fontweight="bold", color="#1B2A4A", pad=20)
    ax.axis("off")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
    
    return fig
