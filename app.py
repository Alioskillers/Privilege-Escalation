"""
app.py
------
Interactive Streamlit web application for Access Control Security Analysis.

This tool helps non-technical users understand:
- Who can access what resources
- Potential privilege escalation risks
- Security vulnerabilities in permission structures
"""

import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import copy

# Import backend modules
from backend.matrix_model import AccessControlMatrix
from backend.privilege_analysis import PrivilegeGraph, NODE_USER, NODE_RESOURCE
from backend.rbac import RBACModel


# ========================================================================
# CONFIGURATION
# ========================================================================

DATA_FILE = Path(__file__).parent / "data" / "sample_permissions.json"
HIGH_PRIVILEGE_RESOURCES = ["file_secret", "db_admin", "service_root"]


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def load_data():
    """Load permission data from JSON file."""
    with open(DATA_FILE) as fh:
        return json.load(fh)


def apply_attack_scenario(data):
    """
    Simulate a security vulnerability by adding a backdoor permission.
    
    Attack scenario: A misconfiguration allows service_user to access db_admin.
    This creates a privilege escalation path for low-privilege users.
    """
    modified_data = copy.deepcopy(data)
    
    # Add backdoor: service_user index → db_admin access
    # In the sample data: resources are ordered, so we need to find indices
    resources = modified_data["resources"]
    
    # Give bob (guest user) access to service that can escalate
    # Add a vulnerability: anyone with service_user can reach db_admin
    # We'll do this by modifying the graph edges later
    
    modified_data["_attack_mode"] = True
    modified_data["_attack_description"] = (
        "🚨 VULNERABILITY INJECTED: A misconfiguration now allows "
        "service_user to indirectly access db_admin through a hidden path."
    )
    
    return modified_data


def create_permission_graph(data, attack_mode=False):
    """Build the permission graph with optional attack scenario."""
    acm = AccessControlMatrix.from_dict(data)
    pg = PrivilegeGraph(acm)
    
    # Add delegation edges if present
    if "delegation" in data:
        pg.add_delegation_edges(data["delegation"])
    
    # ATTACK MODE: Add a backdoor edge (resource → resource)
    if attack_mode:
        # Add hidden path: service_user → db_admin
        if "service_user" in pg.graph and "db_admin" in pg.graph:
            pg.graph.add_edge("service_user", "db_admin", edge_type="vulnerability")
        # Also add: file_public → file_secret
        if "file_public" in pg.graph and "file_secret" in pg.graph:
            pg.graph.add_edge("file_public", "file_secret", edge_type="vulnerability")
    
    return acm, pg


def path_to_natural_language(path, user_name):
    """
    Convert a path list into natural language explanation.
    
    Example:
        ['bob', 'service_user', 'db_admin']
        → "Bob can access service_user, which allows access to db_admin."
    """
    if len(path) <= 1:
        return f"{user_name.title()} has direct access."
    
    # Build the chain
    steps = []
    for i in range(len(path) - 1):
        current = path[i]
        next_item = path[i + 1]
        
        if i == 0:
            # First hop from user
            steps.append(f"{user_name.title()} can access **{next_item}**")
        else:
            # Subsequent hops
            steps.append(f"which connects to **{next_item}**")
    
    return ", ".join(steps[:-1]) + (", " if len(steps) > 1 else "") + steps[-1] + "."


def visualize_graph(pg, highlight_paths=None, attack_mode=False):
    """
    Create a matplotlib visualization of the permission graph.
    
    Args:
        pg: PrivilegeGraph object
        highlight_paths: List of paths to highlight in red
        attack_mode: Whether to show vulnerability edges differently
    
    Returns:
        matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    graph = pg.graph
    
    # Separate users and resources
    user_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == NODE_USER]
    res_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == NODE_RESOURCE]
    
    # Layout: users on left, resources on right
    pos = {}
    for i, u in enumerate(user_nodes):
        pos[u] = (0.0, -i * 1.5)
    for i, r in enumerate(res_nodes):
        pos[r] = (4.0, -i * 1.2)
    
    # Collect edge types
    normal_edges = []
    vulnerability_edges = []
    highlight_edges = set()
    
    if highlight_paths:
        for path in highlight_paths:
            for a, b in zip(path, path[1:]):
                highlight_edges.add((a, b))
    
    for u, v in graph.edges():
        edge_type = graph[u][v].get("edge_type", "permission")
        if (u, v) in highlight_edges:
            continue  # Will draw separately
        elif edge_type == "vulnerability":
            vulnerability_edges.append((u, v))
        else:
            normal_edges.append((u, v))
    
    hot_edges = list(highlight_edges & set(graph.edges()))
    
    # Determine node colors based on danger
    dangerous_resources = set()
    if highlight_paths:
        for path in highlight_paths:
            if path[-1] in HIGH_PRIVILEGE_RESOURCES:
                dangerous_resources.add(path[-1])
    
    user_colors = ["#4C9BE8"] * len(user_nodes)  # Light blue
    res_colors = []
    for r in res_nodes:
        if r in dangerous_resources:
            res_colors.append("#E63946")  # Red for dangerous
        elif r in HIGH_PRIVILEGE_RESOURCES:
            res_colors.append("#FF9800")  # Orange for high-privilege
        else:
            res_colors.append("#66BB6A")  # Green for normal
    
    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, nodelist=user_nodes,
                          node_color=user_colors, node_size=1400, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=res_nodes,
                          node_color=res_colors, node_size=1400, ax=ax)
    nx.draw_networkx_labels(graph, pos, font_size=9, font_color="white",
                           font_weight="bold", ax=ax)
    
    # Draw edges
    if normal_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=normal_edges,
                              edge_color="#888888", arrows=True,
                              arrowsize=20, width=1.5, ax=ax,
                              connectionstyle="arc3,rad=0.05")
    if vulnerability_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=vulnerability_edges,
                              edge_color="#FFA726", arrows=True,
                              arrowsize=20, width=2.0, ax=ax,
                              connectionstyle="arc3,rad=0.1", style="dashed")
    if hot_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=hot_edges,
                              edge_color="#E63946", arrows=True,
                              arrowsize=24, width=3.0, ax=ax,
                              connectionstyle="arc3,rad=0.05")
    
    # Legend
    legend_elements = [
        mpatches.Patch(color="#4C9BE8", label="User"),
        mpatches.Patch(color="#66BB6A", label="Normal Resource"),
        mpatches.Patch(color="#FF9800", label="High-Privilege Resource"),
    ]
    
    if dangerous_resources:
        legend_elements.append(mpatches.Patch(color="#E63946", label="⚠️ Escalation Target"))
    
    if attack_mode:
        legend_elements.append(mpatches.Patch(color="#FFA726", label="🔓 Vulnerability Path"))
    
    ax.legend(handles=legend_elements, loc="lower right", fontsize=10)
    ax.set_title("Access Control Permission Graph", fontsize=14, fontweight="bold", pad=20)
    ax.axis("off")
    plt.tight_layout()
    
    return fig


# ========================================================================
# MAIN APP
# ========================================================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="Access Control Security Simulator",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and introduction
    st.title("🔐 Access Control Security Simulator")
    st.markdown("""
    Welcome to the **Access Control Security Simulator**! This tool helps you understand 
    how permissions work and identify potential security vulnerabilities.
    
    **What you can do:**
    - 🔍 View what resources each user can access
    - ⚠️ Check for privilege escalation risks
    - 📊 Visualize the permission network
    - 🚨 Simulate attack scenarios
    """)
    
    st.divider()
    
    # ====================================================================
    # SIDEBAR
    # ====================================================================
    
    st.sidebar.header("⚙️ Controls")
    
    # Load data
    data = load_data()
    
    # User selection
    users = data["users"]
    selected_user = st.sidebar.selectbox(
        "👤 Select User",
        users,
        help="Choose a user to analyze their permissions and access"
    )
    
    # Analysis type
    analysis_type = st.sidebar.radio(
        "📋 Analysis Type",
        ["View Permissions", "Privilege Escalation", "Graph Visualization", "RBAC Model"],
        help="Choose what analysis to perform"
    )
    
    # Attack scenario toggle
    st.sidebar.divider()
    attack_mode = st.sidebar.checkbox(
        "🚨 Enable Attack Scenario",
        value=False,
        help="Simulate a security vulnerability to demonstrate privilege escalation"
    )
    
    if attack_mode:
        st.sidebar.warning("⚠️ Attack mode enabled! Vulnerabilities have been injected.")
        data = apply_attack_scenario(data)
    
    # System info
    st.sidebar.divider()
    st.sidebar.info(f"""
    **System Info**
    - Total Users: {len(data['users'])}
    - Total Resources: {len(data['resources'])}
    - High-Privilege Resources: {len(HIGH_PRIVILEGE_RESOURCES)}
    """)
    
    # ====================================================================
    # BUILD MODELS
    # ====================================================================
    
    acm, pg = create_permission_graph(data, attack_mode=attack_mode)
    
    # ====================================================================
    # MAIN CONTENT AREA
    # ====================================================================
    
    # ─────────────────────────────────────────────────────────────────
    # 1. VIEW PERMISSIONS
    # ─────────────────────────────────────────────────────────────────
    
    if analysis_type == "View Permissions":
        st.header(f"📂 Permissions for {selected_user.title()}")
        st.markdown(f"""
        This shows all resources that **{selected_user.title()}** can access directly. 
        These permissions are explicitly granted in the access control matrix.
        """)
        
        permissions = acm.get_permissions(selected_user)
        
        if permissions:
            st.success(f"✅ **{selected_user.title()}** has access to {len(permissions)} resource(s):")
            
            # Display as columns
            cols = st.columns(3)
            for idx, perm in enumerate(sorted(permissions)):
                with cols[idx % 3]:
                    # Check if it's a high-privilege resource
                    if perm in HIGH_PRIVILEGE_RESOURCES:
                        st.markdown(f"🔴 **{perm}** (High-Privilege)")
                    else:
                        st.markdown(f"🟢 **{perm}**")
        else:
            st.warning(f"⚠️ **{selected_user.title()}** has no direct permissions.")
        
        # Show reachable resources (via delegation/paths)
        st.divider()
        st.subheader("🔗 Reachable Resources (including indirect access)")
        st.markdown("""
        This includes resources accessible through delegation chains or connected paths.
        """)
        
        reachable = pg.reachable_resources(selected_user)
        if reachable:
            reachable_high = [r for r in reachable if r in HIGH_PRIVILEGE_RESOURCES]
            reachable_normal = [r for r in reachable if r not in HIGH_PRIVILEGE_RESOURCES]
            
            if reachable_high:
                st.error(f"⚠️ Can reach {len(reachable_high)} HIGH-PRIVILEGE resource(s):")
                for r in sorted(reachable_high):
                    st.markdown(f"  - 🔴 **{r}**")
            
            if reachable_normal:
                st.info(f"ℹ️ Can reach {len(reachable_normal)} additional resource(s):")
                for r in sorted(reachable_normal):
                    st.markdown(f"  - 🟢 **{r}**")
        else:
            st.info(f"ℹ️ No additional resources reachable beyond direct permissions.")
    
    # ─────────────────────────────────────────────────────────────────
    # 2. PRIVILEGE ESCALATION ANALYSIS
    # ─────────────────────────────────────────────────────────────────
    
    elif analysis_type == "Privilege Escalation":
        st.header(f"⚠️ Privilege Escalation Analysis: {selected_user.title()}")
        st.markdown(f"""
        This analysis checks if **{selected_user.title()}** can reach any high-privilege 
        resources through indirect paths (a security risk known as **privilege escalation**).
        
        **High-privilege resources:** {', '.join(HIGH_PRIVILEGE_RESOURCES)}
        """)
        
        if attack_mode:
            st.error(data.get("_attack_description", "Attack mode enabled"))
        
        st.divider()
        
        # Detect escalation paths
        escalation_paths = pg.detect_escalation_paths([selected_user], HIGH_PRIVILEGE_RESOURCES)
        
        if escalation_paths:
            st.error(f"🚨 **SECURITY RISK DETECTED!** {len(escalation_paths)} escalation path(s) found.")
            
            st.markdown("### Escalation Paths Found:")
            
            for idx, path_info in enumerate(escalation_paths, 1):
                path = path_info["path"]
                target = path_info["resource"]
                via_delegation = path_info["via_delegation"]
                
                with st.expander(f"Path {idx}: {selected_user.title()} → {target}", expanded=(idx == 1)):
                    # Natural language explanation
                    st.markdown("**Explanation:**")
                    explanation = path_to_natural_language(path, selected_user)
                    st.info(explanation)
                    
                    # Technical details
                    st.markdown("**Technical Path:**")
                    path_str = " → ".join(path)
                    st.code(path_str, language="text")
                    
                    # Metadata
                    cols = st.columns(2)
                    with cols[0]:
                        st.metric("Hops", path_info["hops"])
                    with cols[1]:
                        delegation_tag = "Yes ⚠️" if via_delegation else "No"
                        st.metric("Via Delegation", delegation_tag)
                    
                    # Recommendation
                    st.markdown("**Recommendation:**")
                    st.warning(f"""
                    Remove intermediate permissions or add access controls to prevent 
                    **{selected_user}** from reaching **{target}**.
                    """)
        else:
            st.success(f"✅ **No privilege escalation detected** for {selected_user.title()}.")
            st.markdown(f"""
            **{selected_user.title()}** cannot access any high-privilege resources through 
            direct or indirect paths. The current permissions are secure for this user.
            """)
        
        # Show what high-privilege resources exist
        st.divider()
        st.subheader("🔐 High-Privilege Resources in System")
        cols = st.columns(len(HIGH_PRIVILEGE_RESOURCES))
        for idx, res in enumerate(HIGH_PRIVILEGE_RESOURCES):
            with cols[idx]:
                # Check who has access
                authorized_users = [u for u in users if acm.has_permission(u, res)]
                st.metric(
                    label=res,
                    value=len(authorized_users),
                    delta=f"{len(authorized_users)} user(s)",
                    delta_color="inverse"
                )
    
    # ─────────────────────────────────────────────────────────────────
    # 3. GRAPH VISUALIZATION
    # ─────────────────────────────────────────────────────────────────
    
    elif analysis_type == "Graph Visualization":
        st.header("📊 Permission Graph Visualization")
        st.markdown("""
        This interactive graph shows the relationships between users and resources.
        
        **Legend:**
        - 🔵 **Blue nodes** = Users
        - 🟢 **Green nodes** = Normal resources  
        - 🟠 **Orange nodes** = High-privilege resources
        - 🔴 **Red nodes** = Escalation targets (security risk)
        - 🔴 **Red arrows** = Escalation paths
        """)
        
        if attack_mode:
            st.warning("🚨 Vulnerability paths are shown in dashed orange lines.")
        
        st.divider()
        
        # Generate visualization
        escalation_paths = pg.detect_escalation_paths([selected_user], HIGH_PRIVILEGE_RESOURCES)
        highlight_paths = [p["path"] for p in escalation_paths] if escalation_paths else None
        
        fig = visualize_graph(pg, highlight_paths=highlight_paths, attack_mode=attack_mode)
        st.pyplot(fig)
        plt.close()
        
        # Graph statistics
        st.divider()
        st.subheader("📈 Graph Statistics")
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Nodes", pg.graph.number_of_nodes())
        with cols[1]:
            st.metric("Total Edges", pg.graph.number_of_edges())
        with cols[2]:
            user_count = len([n for n, d in pg.graph.nodes(data=True) if d.get("node_type") == NODE_USER])
            st.metric("Users", user_count)
        with cols[3]:
            resource_count = len([n for n, d in pg.graph.nodes(data=True) if d.get("node_type") == NODE_RESOURCE])
            st.metric("Resources", resource_count)
    
    # ─────────────────────────────────────────────────────────────────
    # 4. RBAC MODEL
    # ─────────────────────────────────────────────────────────────────
    
    elif analysis_type == "RBAC Model":
        st.header("👥 Role-Based Access Control (RBAC) Model")
        st.markdown("""
        **RBAC** simplifies permission management by grouping permissions into roles, 
        then assigning roles to users.
        
        **How it works:**
        1. Define **roles** (e.g., Admin, Developer, Guest)
        2. Assign **permissions** to each role
        3. Assign **roles** to users
        4. Users inherit all permissions from their roles
        """)
        
        st.divider()
        
        # Build RBAC model
        rbac = RBACModel.from_dict(data)
        
        # Show selected user's roles and permissions
        st.subheader(f"🔍 RBAC Analysis: {selected_user.title()}")
        
        user_roles = data["rbac"]["user_roles"].get(selected_user, [])
        if user_roles:
            st.success(f"**{selected_user.title()}** has {len(user_roles)} role(s):")
            
            for role in user_roles:
                with st.expander(f"Role: {role.title()}", expanded=True):
                    role_perms = data["rbac"]["roles"][role]
                    st.markdown(f"**Permissions ({len(role_perms)}):**")
                    
                    # Categorize permissions
                    high_priv = [p for p in role_perms if p in HIGH_PRIVILEGE_RESOURCES]
                    normal_priv = [p for p in role_perms if p not in HIGH_PRIVILEGE_RESOURCES]
                    
                    if high_priv:
                        st.error(f"🔴 High-Privilege: {', '.join(high_priv)}")
                    if normal_priv:
                        st.info(f"🟢 Normal: {', '.join(normal_priv)}")
            
            # Effective permissions
            effective = rbac.effective_permissions(selected_user)
            st.divider()
            st.markdown(f"**Effective Permissions (Union of all roles):** {len(effective)}")
            st.code(", ".join(sorted(effective)), language="text")
        else:
            st.warning(f"⚠️ **{selected_user.title()}** has no assigned roles.")
        
        # Show all roles
        st.divider()
        st.subheader("📋 All Roles in System")
        
        roles_data = data["rbac"]["roles"]
        for role_name, perms in roles_data.items():
            with st.expander(f"Role: {role_name.title()} ({len(perms)} permissions)"):
                # Show which users have this role
                users_with_role = [u for u, r in data["rbac"]["user_roles"].items() if role_name in r]
                st.markdown(f"**Assigned to:** {', '.join([u.title() for u in users_with_role]) if users_with_role else 'No users'}")
                
                st.markdown(f"**Permissions:**")
                st.code(", ".join(sorted(perms)), language="text")
        
        # ACM derived from RBAC
        st.divider()
        st.subheader("🔄 Access Control Matrix (Derived from RBAC)")
        st.markdown("This shows the final permission matrix after expanding all roles:")
        
        rbac_acm = rbac.build_acm()
        
        # Display as a table
        import pandas as pd
        df = pd.DataFrame(
            rbac_acm.matrix,
            index=rbac_acm.users,
            columns=rbac_acm.resources
        )
        # Replace 1/0 with ✓/✗
        df = df.replace({1: "✓", 0: "✗"})
        st.dataframe(df, use_container_width=True)
    
    # ====================================================================
    # FOOTER
    # ====================================================================
    
    st.divider()
    st.markdown("""
    ---
    **About this tool:** This simulator demonstrates access control concepts and security vulnerabilities. 
    It uses graph theory (NetworkX) and matrix algebra (NumPy) to analyze permission structures.
    
    💡 **Tip:** Enable "Attack Scenario" to see how a single misconfiguration can create security risks!
    """)


# ========================================================================
# RUN APP
# ========================================================================

if __name__ == "__main__":
    main()
