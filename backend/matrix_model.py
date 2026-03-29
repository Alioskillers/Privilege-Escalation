"""
matrix_model.py
---------------
Core Access Control Matrix (ACM) representation and boolean matrix algebra.

The ACM is a 2-D binary matrix where:
  - Rows  → subjects (users)
  - Cols  → objects  (resources)
  - Cell  → 1 if the subject holds access to the object, else 0
"""

import json
import numpy as np


class AccessControlMatrix:
    """
    Represents an Access Control Matrix and exposes boolean matrix algebra
    operations needed for transitive-closure / privilege-escalation analysis.
    """

    def __init__(self, users: list[str], resources: list[str], matrix: np.ndarray):
        """
        Parameters
        ----------
        users     : ordered list of subject (user) names
        resources : ordered list of object (resource) names
        matrix    : binary numpy array of shape (len(users), len(resources))
        """
        if matrix.shape != (len(users), len(resources)):
            raise ValueError(
                f"Matrix shape {matrix.shape} does not match "
                f"({len(users)} users × {len(resources)} resources)."
            )
        self.users = users
        self.resources = resources
        self.matrix = matrix.astype(np.int8)

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "AccessControlMatrix":
        """Build an ACM from the canonical JSON/dict format used in this project."""
        users = data["users"]
        resources = data["resources"]
        rows = [data["permissions"][u] for u in users]
        matrix = np.array(rows, dtype=np.int8)
        return cls(users, resources, matrix)

    @classmethod
    def from_json_file(cls, path: str) -> "AccessControlMatrix":
        """Load an ACM directly from a JSON file on disk."""
        with open(path, "r") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    # ------------------------------------------------------------------
    # Boolean matrix algebra
    # ------------------------------------------------------------------

    @staticmethod
    def bool_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Boolean (logical) matrix multiplication.

        Each cell (i, j) of the result is 1 iff there exists at least one k
        such that a[i,k] == 1  AND  b[k,j] == 1.

        This is equivalent to  (A @ B) > 0  for binary matrices, but we use
        the explicit numpy logical path to stay numerically clean.
        """
        return np.clip(a @ b, 0, 1).astype(np.int8)

    @staticmethod
    def bool_add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Element-wise boolean OR of two same-shaped binary matrices."""
        return np.clip(a + b, 0, 1).astype(np.int8)

    def power(self, n: int) -> np.ndarray:
        """
        Compute A^n under boolean matrix multiplication.

        A^1 = A
        A^k = A^(k-1) * A   (boolean multiply)

        Requires a square (user × user) matrix.  If the ACM is not square,
        callers should work with the derived square permission-propagation
        matrix instead.
        """
        if self.matrix.shape[0] != self.matrix.shape[1]:
            raise ValueError("Matrix power requires a square matrix.")
        result = self.matrix.copy()
        for _ in range(n - 1):
            result = self.bool_multiply(result, self.matrix)
        return result

    def transitive_closure(self) -> np.ndarray:
        """
        Compute the transitive closure of the matrix using Warshall's algorithm.

        For a rectangular ACM (users × resources) the closure is computed on
        the augmented *square* adjacency matrix that represents the full
        subject–object graph, then the user-rows × resource-cols sub-block is
        returned.

        The augmented node ordering is:  users first, then resources.
        """
        n_users = len(self.users)
        n_res = len(self.resources)
        n = n_users + n_res

        # Build the square adjacency matrix for the combined graph
        adj = np.zeros((n, n), dtype=np.int8)
        adj[:n_users, n_users:] = self.matrix  # user → resource edges

        # Warshall's algorithm
        closure = adj.copy()
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    closure[i, j] = closure[i, j] or (closure[i, k] and closure[k, j])

        # Return the user-rows × resource-cols sub-block
        return closure[:n_users, n_users:]

    # ------------------------------------------------------------------
    # Accessors / display helpers
    # ------------------------------------------------------------------

    def user_index(self, user: str) -> int:
        return self.users.index(user)

    def resource_index(self, resource: str) -> int:
        return self.resources.index(resource)

    def get_permissions(self, user: str) -> list[str]:
        """Return the list of resources accessible by *user*."""
        idx = self.user_index(user)
        return [r for r, v in zip(self.resources, self.matrix[idx]) if v]

    def has_permission(self, user: str, resource: str) -> bool:
        return bool(self.matrix[self.user_index(user), self.resource_index(resource)])

    def __repr__(self) -> str:  # pragma: no cover
        header = f"{'':12}" + "  ".join(f"{r:12}" for r in self.resources)
        rows = [header]
        for u, row in zip(self.users, self.matrix):
            rows.append(f"{u:12}" + "  ".join(f"{v:12}" for v in row))
        return "\n".join(rows)
