"""
main.py
-------
Entry point for the Access Control Matrix (ACM) security analysis tool.

Pipeline:
  1. Load permissions from JSON
  2. Build the Access Control Matrix
  3. Compute boolean matrix powers and transitive closure
  4. Detect privilege escalation paths via the permission graph
  5. Build and display the RBAC model
  6. Visualise the permission graph (saved as PNG)
"""

import json
import sys
from pathlib import Path

from matrix_model import AccessControlMatrix
from privilege_analysis import PrivilegeGraph
from rbac import RBACModel
from utils import (
    print_section,
    print_matrix,
    print_matrix_powers,
    print_closure_diff,
    visualise_permission_graph,
)

DATA_FILE = Path(__file__).parent / "data" / "sample_permissions.json"
GRAPH_OUT = Path(__file__).parent / "permission_graph.png"


def main() -> None:
    # ── 1. Load data ─────────────────────────────────────────────────
    print_section("1 · Loading permissions")
    with open(DATA_FILE) as fh:
        data = json.load(fh)
    print(f"  File    : {DATA_FILE}")
    print(f"  Users   : {data['users']}")
    print(f"  Resources: {data['resources']}")

    # ── 2. Build Access Control Matrix ───────────────────────────────
    print_section("2 · Access Control Matrix (ACM)")
    acm = AccessControlMatrix.from_dict(data)
    print_matrix(
        acm.matrix,
        row_labels=acm.users,
        col_labels=acm.resources,
        title="Original ACM  (✓ = access granted)",
    )

    # Per-user permission listing
    print("  Per-user permissions:")
    for user in acm.users:
        perms = acm.get_permissions(user)
        tag = perms if perms else ["(none)"]
        print(f"    {user:8} → {tag}")

    # ── 3. Boolean matrix algebra ─────────────────────────────────────
    print_section("3 · Boolean Matrix Algebra")

    # Build a square user-user adjacency via user→resource→user for powers demo
    # (real power analysis on user-user delegation would need a square matrix;
    #  we demonstrate on a minimal square sub-matrix derived from shared resources)
    n = len(acm.users)
    # user-user reachability: user i can reach user j if they share ≥1 resource
    user_user = (acm.matrix @ acm.matrix.T).clip(0, 1)

    import numpy as np
    uu_acm = AccessControlMatrix(acm.users, acm.users, user_user)
    print("  Square user-user co-access matrix (A):  user i shares a resource with user j")
    print_matrix(user_user, acm.users, acm.users, title="User-User Co-access  A")
    print("  Computing boolean powers A^1 … A^3 …")
    print_matrix_powers(uu_acm, max_power=3)

    # ── 4. Transitive closure ─────────────────────────────────────────
    print_section("4 · Transitive Closure")
    closure = acm.transitive_closure()
    print_matrix(
        closure,
        row_labels=acm.users,
        col_labels=acm.resources,
        title="Transitive Closure  (reachable via delegation chains)",
    )
    print_closure_diff(acm.matrix, closure, acm.users, acm.resources)

    # ── 5. Privilege escalation detection ────────────────────────────
    print_section("5 · Privilege Escalation Detection")
    pg = PrivilegeGraph(acm)

    # Wire in delegation edges from the JSON data
    if "delegation" in data:
        pg.add_delegation_edges(data["delegation"])
        print("  Delegation edges added from config.")

    pg.print_graph_summary()

    low_users = data.get("low_privilege_users", [])
    high_res  = data.get("high_privilege_resources", [])

    # Show reachable resources for each low-privilege user
    print("  Reachable resources (direct + via delegation):")
    for user in low_users:
        reachable = pg.reachable_resources(user)
        print(f"    {user:8} → {reachable if reachable else ['(none)']}")

    pg.print_escalation_report(low_users, high_res)

    # ── 6. RBAC model ─────────────────────────────────────────────────
    print_section("6 · Role-Based Access Control (RBAC)")
    rbac = RBACModel.from_dict(data)
    rbac.set_resources(data["resources"])
    rbac.print_summary()

    rbac_acm = rbac.build_acm()
    print_matrix(
        rbac_acm.matrix,
        row_labels=rbac_acm.users,
        col_labels=rbac_acm.resources,
        title="ACM derived from RBAC",
    )

    # ── 7. Visualise ──────────────────────────────────────────────────
    print_section("7 · Graph Visualisation")

    # Gather escalation paths for highlighting
    esc_paths = pg.detect_escalation_paths(low_users, high_res)
    highlight = [e["path"] for e in esc_paths]

    visualise_permission_graph(
        pg.graph,
        output_path=str(GRAPH_OUT),
        highlight_paths=highlight,
    )

    print("\n  ✅  Analysis complete.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
