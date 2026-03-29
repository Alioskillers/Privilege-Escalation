"""
rbac.py
-------
Role-Based Access Control (RBAC) model.

Structure:
  - Role  : a named set of resource permissions
  - RBACModel : maps users → roles → permissions and can export an ACM
"""

from __future__ import annotations
import json
import numpy as np
from .matrix_model import AccessControlMatrix


class Role:
    """A named collection of resource permissions."""

    def __init__(self, name: str, permissions: list[str]):
        self.name = name
        self.permissions: set[str] = set(permissions)

    def __repr__(self) -> str:
        return f"Role(name={self.name!r}, permissions={sorted(self.permissions)})"


class RBACModel:
    """
    Full RBAC model: roles carry resource permissions, users carry roles.

    Can automatically derive an AccessControlMatrix for the full resource
    universe by expanding user → role → resource mappings.
    """

    def __init__(self):
        self.roles: dict[str, Role] = {}
        self.user_roles: dict[str, list[str]] = {}  # user → [role names]
        self.resources: list[str] = []

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def add_role(self, name: str, permissions: list[str]) -> None:
        """Register a named role with its list of allowed resource names."""
        self.roles[name] = Role(name, permissions)

    def assign_role(self, user: str, role_name: str) -> None:
        """Assign *role_name* to *user*.  A user may hold multiple roles."""
        if role_name not in self.roles:
            raise KeyError(f"Role '{role_name}' is not defined.")
        self.user_roles.setdefault(user, [])
        if role_name not in self.user_roles[user]:
            self.user_roles[user].append(role_name)

    def set_resources(self, resources: list[str]) -> None:
        """Set the canonical ordered list of resources in the system."""
        self.resources = list(resources)

    @classmethod
    def from_dict(cls, data: dict) -> "RBACModel":
        """
        Build an RBACModel from the 'rbac' sub-section of the JSON config.

        Expected shape:
          {
            "roles":      { "<role>": ["<resource>", ...], ... },
            "user_roles": { "<user>": ["<role>", ...], ... }
          }
        """
        model = cls()
        model.set_resources(data.get("resources", []))

        rbac = data["rbac"]
        for role_name, perms in rbac["roles"].items():
            model.add_role(role_name, perms)

        for user, roles in rbac["user_roles"].items():
            for role in roles:
                model.assign_role(user, role)

        return model

    @classmethod
    def from_json_file(cls, path: str) -> "RBACModel":
        with open(path, "r") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    # ------------------------------------------------------------------
    # ACM derivation
    # ------------------------------------------------------------------

    def build_acm(self) -> AccessControlMatrix:
        """
        Derive an AccessControlMatrix from the current RBAC configuration.

        A user is granted access to a resource if *any* of their roles
        includes that resource (union of role permissions).
        """
        if not self.resources:
            # Collect all mentioned resources from roles if not explicitly set
            all_res: set[str] = set()
            for role in self.roles.values():
                all_res.update(role.permissions)
            self.resources = sorted(all_res)

        users = sorted(self.user_roles.keys())
        matrix = np.zeros((len(users), len(self.resources)), dtype=np.int8)

        for u_idx, user in enumerate(users):
            # Collect the union of all permissions across the user's roles
            allowed: set[str] = set()
            for role_name in self.user_roles.get(user, []):
                allowed.update(self.roles[role_name].permissions)
            for r_idx, resource in enumerate(self.resources):
                matrix[u_idx, r_idx] = 1 if resource in allowed else 0

        return AccessControlMatrix(users, self.resources, matrix)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def effective_permissions(self, user: str) -> set[str]:
        """Return the union of all resource permissions held by *user*."""
        perms: set[str] = set()
        for role_name in self.user_roles.get(user, []):
            perms.update(self.roles[role_name].permissions)
        return perms

    def print_summary(self) -> None:
        """Print a human-readable RBAC summary."""
        print("\n── RBAC Model Summary ────────────────────────────────────")
        print(f"  Roles    : {', '.join(self.roles)}")
        print(f"  Users    : {', '.join(self.user_roles)}")
        print()
        for user, roles in self.user_roles.items():
            perms = self.effective_permissions(user)
            print(f"  {user:10}  roles={roles}  →  {sorted(perms)}")
        print("──────────────────────────────────────────────────────────\n")
