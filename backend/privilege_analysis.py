"""
privilege_analysis.py
---------------------
Privilege escalation detection using NetworkX directed graphs.

Workflow:
  1. Convert the ACM to a directed permission graph.
  2. Optionally layer in delegation edges (user → user).
  3. Walk all simple paths from low-privilege users to high-privilege
     resources and report escalation chains.
"""

import networkx as nx
from .matrix_model import AccessControlMatrix


# Node-type tags used as graph attributes
NODE_USER = "user"
NODE_RESOURCE = "resource"


class PrivilegeGraph:
    """
    A directed graph that encodes who can reach what, with optional
    delegation / role-inheritance edges between users.
    """

    def __init__(self, acm: AccessControlMatrix):
        self.acm = acm
        self.graph: nx.DiGraph = nx.DiGraph()
        self._build_graph()

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self) -> None:
        """Populate nodes and direct permission edges from the ACM."""
        # Add user nodes
        for user in self.acm.users:
            self.graph.add_node(user, node_type=NODE_USER)

        # Add resource nodes
        for resource in self.acm.resources:
            self.graph.add_node(resource, node_type=NODE_RESOURCE)

        # Add permission edges: user → resource
        for u_idx, user in enumerate(self.acm.users):
            for r_idx, resource in enumerate(self.acm.resources):
                if self.acm.matrix[u_idx, r_idx] == 1:
                    self.graph.add_edge(user, resource, edge_type="permission")

    def add_delegation_edges(self, delegation: dict[str, list[str]]) -> None:
        """
        Add user → user delegation edges.

        If carol delegates to alice, alice inherits carol's reachable resources
        when computing transitive paths.

        Parameters
        ----------
        delegation : mapping  delegator → [list of delegates]
                     Keys are raw strings like "carol_can_delegate_to".
        """
        for key, delegates in delegation.items():
            # Key format: "<user>_can_delegate_to"
            delegator = key.replace("_can_delegate_to", "")
            if delegator not in self.acm.users:
                continue
            for delegate in delegates:
                if delegate in self.acm.users:
                    self.graph.add_edge(delegator, delegate, edge_type="delegation")

    # ------------------------------------------------------------------
    # Escalation detection
    # ------------------------------------------------------------------

    def detect_escalation_paths(
        self,
        low_privilege_users: list[str],
        high_privilege_resources: list[str],
    ) -> list[dict]:
        """
        Find all simple paths from low-privilege users to high-privilege
        resources in the permission/delegation graph.

        Returns a list of result dicts, one per discovered path:
            {
                "user":     <source user>,
                "resource": <target resource>,
                "path":     [node, node, …],
                "hops":     <number of edges>,
                "via_delegation": <bool>
            }
        """
        escalation_paths = []

        for user in low_privilege_users:
            if user not in self.graph:
                continue
            for resource in high_privilege_resources:
                if resource not in self.graph:
                    continue
                # nx.all_simple_paths explores *all* paths; cut at depth 6
                for path in nx.all_simple_paths(self.graph, source=user, target=resource, cutoff=6):
                    via_delegation = any(
                        self.graph[path[i]][path[i + 1]].get("edge_type") == "delegation"
                        for i in range(len(path) - 1)
                    )
                    escalation_paths.append(
                        {
                            "user": user,
                            "resource": resource,
                            "path": path,
                            "hops": len(path) - 1,
                            "via_delegation": via_delegation,
                        }
                    )

        return escalation_paths

    def reachable_resources(self, user: str) -> list[str]:
        """
        Return all resources reachable from *user* (including via delegation
        chains) using graph reachability.
        """
        if user not in self.graph:
            return []
        reachable = nx.descendants(self.graph, user)
        return [n for n in reachable if self.graph.nodes[n].get("node_type") == NODE_RESOURCE]

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def print_escalation_report(
        self,
        low_privilege_users: list[str],
        high_privilege_resources: list[str],
    ) -> None:
        """Pretty-print a full privilege escalation report to stdout."""
        paths = self.detect_escalation_paths(low_privilege_users, high_privilege_resources)

        print("\n" + "=" * 65)
        print("  PRIVILEGE ESCALATION ANALYSIS REPORT")
        print("=" * 65)
        print(f"  Low-privilege users      : {', '.join(low_privilege_users)}")
        print(f"  High-privilege resources : {', '.join(high_privilege_resources)}")
        print(f"  Escalation paths found   : {len(paths)}")
        print("=" * 65)

        if not paths:
            print("  ✅  No privilege escalation paths detected.")
        else:
            for i, entry in enumerate(paths, 1):
                tag = " [via delegation]" if entry["via_delegation"] else ""
                arrow_path = " → ".join(entry["path"])
                print(f"\n  [{i}] {entry['user']} ──► {entry['resource']}{tag}")
                print(f"       Path ({entry['hops']} hop(s)): {arrow_path}")

        print("\n" + "=" * 65 + "\n")

    def print_graph_summary(self) -> None:
        """Print a compact summary of the permission graph."""
        print("\n── Permission Graph Summary ──────────────────────────────")
        print(f"  Nodes : {self.graph.number_of_nodes()}")
        print(f"  Edges : {self.graph.number_of_edges()}")
        user_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == NODE_USER]
        res_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == NODE_RESOURCE]
        print(f"  Users     : {', '.join(user_nodes)}")
        print(f"  Resources : {', '.join(res_nodes)}")
        print("──────────────────────────────────────────────────────────\n")
