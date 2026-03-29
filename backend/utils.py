"""
utils.py
--------
Display and visualisation utilities shared across the project.
"""

from __future__ import annotations

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")          # non-interactive backend – no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

from .matrix_model import AccessControlMatrix


# ── Console formatting ────────────────────────────────────────────────

def print_matrix(
    matrix: np.ndarray,
    row_labels: list[str],
    col_labels: list[str],
    title: str = "Matrix",
) -> None:
    """Pretty-print a binary matrix to stdout with row/column labels."""
    col_w = max(max((len(c) for c in col_labels), default=4), 4)
    row_w = max(max((len(r) for r in row_labels), default=6), 6)

    print(f"\n── {title} {'─' * max(0, 55 - len(title))}")
    # Header row
    header = f"{'':>{row_w}}  " + "  ".join(f"{c:>{col_w}}" for c in col_labels)
    print(header)
    print("  " + "─" * (len(header) - 2))
    for label, row in zip(row_labels, matrix):
        cells = "  ".join(f"{'✓' if v else '·':>{col_w}}" for v in row)
        print(f"{label:>{row_w}}  {cells}")
    print()


def print_section(title: str) -> None:
    """Print a prominent section header."""
    bar = "═" * 65
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}")


def print_matrix_powers(acm: AccessControlMatrix, max_power: int = 3) -> None:
    """
    Compute and display A^1 … A^max_power for a square ACM.
    Falls back gracefully if the matrix is not square.
    """
    if acm.matrix.shape[0] != acm.matrix.shape[1]:
        print("  (Matrix is not square – skipping power computation)\n")
        return

    for n in range(1, max_power + 1):
        m = acm.power(n)
        print_matrix(m, acm.users, acm.users, title=f"A^{n}  (Boolean Power)")


# ── Graph visualisation ───────────────────────────────────────────────

def visualise_permission_graph(
    graph: nx.DiGraph,
    output_path: str = "permission_graph.png",
    highlight_paths: list[list[str]] | None = None,
) -> None:
    """
    Render the permission graph to a PNG file.

    Parameters
    ----------
    graph         : the NetworkX DiGraph from PrivilegeGraph
    output_path   : where to write the PNG
    highlight_paths : optional list of node-paths to draw in red
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    # Separate users from resources for layout
    user_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "user"]
    res_nodes  = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "resource"]

    # Two-column layout: users on the left, resources on the right
    pos: dict[str, tuple[float, float]] = {}
    for i, u in enumerate(user_nodes):
        pos[u] = (0.0, -i * 1.5)
    for i, r in enumerate(res_nodes):
        pos[r] = (4.0, -i * 1.5)

    # Collect highlighted edges
    highlight_edges: set[tuple[str, str]] = set()
    if highlight_paths:
        for path in highlight_paths:
            for a, b in zip(path, path[1:]):
                highlight_edges.add((a, b))

    normal_edges = [(u, v) for u, v in graph.edges() if (u, v) not in highlight_edges]
    hot_edges    = list(highlight_edges & set(graph.edges()))

    # Draw
    nx.draw_networkx_nodes(graph, pos, nodelist=user_nodes,
                           node_color="#4C9BE8", node_size=1200, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=res_nodes,
                           node_color="#F4A261", node_size=1200, ax=ax)
    nx.draw_networkx_labels(graph, pos, font_size=8, font_color="white",
                            font_weight="bold", ax=ax)
    nx.draw_networkx_edges(graph, pos, edgelist=normal_edges,
                           edge_color="#888888", arrows=True,
                           arrowsize=18, width=1.2, ax=ax,
                           connectionstyle="arc3,rad=0.05")
    if hot_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=hot_edges,
                               edge_color="#E63946", arrows=True,
                               arrowsize=22, width=2.5, ax=ax,
                               connectionstyle="arc3,rad=0.05")

    # Legend
    legend_handles = [
        mpatches.Patch(color="#4C9BE8", label="User"),
        mpatches.Patch(color="#F4A261", label="Resource"),
        mpatches.Patch(color="#E63946", label="Escalation path"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=9)
    ax.set_title("Access Control – Permission Graph", fontsize=13, pad=14)
    ax.axis("off")
    plt.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out), dpi=150)
    plt.close(fig)
    print(f"  📊  Graph saved to: {out.resolve()}")


# ── Transitive-closure diff ──────────────────────────────────────────

def print_closure_diff(
    original: np.ndarray,
    closure: np.ndarray,
    users: list[str],
    resources: list[str],
) -> None:
    """
    Show which new (user, resource) accesses the transitive closure reveals
    beyond the original ACM.
    """
    gained = np.clip(closure - original, 0, 1)
    if not gained.any():
        print("  ✅  Transitive closure adds no new permissions.\n")
        return

    print("  ⚠️   Permissions implied by transitive closure (not in original ACM):")
    for u_idx, user in enumerate(users):
        for r_idx, resource in enumerate(resources):
            if gained[u_idx, r_idx]:
                print(f"       {user}  →  {resource}")
    print()
