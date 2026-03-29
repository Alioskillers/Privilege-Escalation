# 📸 App Interface Preview

## What the Streamlit App Looks Like

### Main Interface
```
┌────────────────────────────────────────────────────────────────────┐
│  🔐 Access Control Security Simulator                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Welcome to the Access Control Security Simulator!                │
│  This tool helps you understand how permissions work and          │
│  identify potential security vulnerabilities.                     │
│                                                                    │
│  What you can do:                                                 │
│  🔍 View what resources each user can access                      │
│  ⚠️  Check for privilege escalation risks                         │
│  📊 Visualize the permission network                              │
│  🚨 Simulate attack scenarios                                     │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
```

### Sidebar (Control Panel)
```
┌─────────────────────────┐
│  ⚙️ Controls            │
├─────────────────────────┤
│                         │
│  👤 Select User         │
│  ▼ [bob]                │
│                         │
│  📋 Analysis Type       │
│  ○ View Permissions     │
│  ● Privilege Escalation │
│  ○ Graph Visualization  │
│  ○ RBAC Model           │
│                         │
│ ─────────────────────── │
│                         │
│  ☑️ Enable Attack       │
│     Scenario            │
│                         │
│  ⚠️ Attack mode enabled!│
│  Vulnerabilities have   │
│  been injected.         │
│                         │
│ ─────────────────────── │
│                         │
│  ℹ️ System Info         │
│  Total Users: 5         │
│  Total Resources: 6     │
│  High-Privilege: 3      │
│                         │
└─────────────────────────┘
```

### View Permissions Mode
```
┌────────────────────────────────────────────────────────────────────┐
│  📂 Permissions for Bob                                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  This shows all resources that Bob can access directly.           │
│  These permissions are explicitly granted in the access control   │
│  matrix.                                                           │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ ✅ Bob has access to 2 resource(s):                          │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  🟢 file_public    🟢 service_user                                │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  🔗 Reachable Resources (including indirect access)               │
│  This includes resources accessible through delegation chains...  │
│                                                                    │
│  ℹ️ Can reach 2 additional resource(s):                           │
│    - 🟢 file_public                                               │
│    - 🟢 service_user                                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Privilege Escalation Mode (Attack Enabled)
```
┌────────────────────────────────────────────────────────────────────┐
│  ⚠️ Privilege Escalation Analysis: Bob                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  This analysis checks if Bob can reach any high-privilege         │
│  resources through indirect paths (a security risk known as       │
│  privilege escalation).                                           │
│                                                                    │
│  High-privilege resources: file_secret, db_admin, service_root    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🚨 VULNERABILITY INJECTED: A misconfiguration now allows     │ │
│  │ service_user to indirectly access db_admin through a hidden  │ │
│  │ path.                                                         │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🚨 SECURITY RISK DETECTED! 2 escalation path(s) found.      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Escalation Paths Found:                                          │
│                                                                    │
│  ▼ Path 1: Bob → db_admin                                        │
│  │                                                                │
│  │  Explanation:                                                  │
│  │  ┌────────────────────────────────────────────────────────┐  │
│  │  │ ℹ️ Bob can access service_user, which connects to     │  │
│  │  │    db_admin.                                           │  │
│  │  └────────────────────────────────────────────────────────┘  │
│  │                                                                │
│  │  Technical Path:                                               │
│  │  bob → service_user → db_admin                                │
│  │                                                                │
│  │  Hops: 2          Via Delegation: No                          │
│  │                                                                │
│  │  Recommendation:                                               │
│  │  ⚠️ Remove intermediate permissions or add access controls    │
│  │     to prevent bob from reaching db_admin.                    │
│  └────────────────────────────────────────────────────────────── │
│                                                                    │
│  ▼ Path 2: Bob → file_secret                                     │
│     [Similar format...]                                           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Graph Visualization Mode
```
┌────────────────────────────────────────────────────────────────────┐
│  📊 Permission Graph Visualization                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  This interactive graph shows the relationships between users     │
│  and resources.                                                   │
│                                                                    │
│  Legend:                                                          │
│  🔵 Blue nodes = Users                                            │
│  🟢 Green nodes = Normal resources                                │
│  🟠 Orange nodes = High-privilege resources                       │
│  🔴 Red nodes = Escalation targets                                │
│  🔴 Red arrows = Escalation paths                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ ⚠️ Vulnerability paths are shown in dashed orange lines      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  [Interactive Graph Display Here]                                 │
│                                                                    │
│   alice ────→ file_public                                         │
│     │                                                              │
│     └─────→ service_user                                          │
│                                                                    │
│   bob ──────→ file_public                                         │
│     │                                                              │
│     └─────→ service_user ═══╗ (vulnerability)                     │
│                             ║                                      │
│   carol ────→ [ALL RESOURCES]                                     │
│                             ║                                      │
│   dave ─────→ db_readonly   ║                                     │
│                             ▼                                      │
│   eve ──────→ file_public   db_admin (🔴 ESCALATION TARGET)      │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  📈 Graph Statistics                                              │
│                                                                    │
│  Total Nodes: 11    Total Edges: 15    Users: 5    Resources: 6  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### RBAC Model Mode
```
┌────────────────────────────────────────────────────────────────────┐
│  👥 Role-Based Access Control (RBAC) Model                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  RBAC simplifies permission management by grouping permissions    │
│  into roles, then assigning roles to users.                       │
│                                                                    │
│  How it works:                                                    │
│  1. Define roles (e.g., Admin, Developer, Guest)                 │
│  2. Assign permissions to each role                              │
│  3. Assign roles to users                                        │
│  4. Users inherit all permissions from their roles               │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  🔍 RBAC Analysis: Bob                                            │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ ✅ Bob has 1 role(s):                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ▼ Role: Guest                                                    │
│  │                                                                │
│  │  Permissions (1):                                              │
│  │  🟢 Normal: file_public                                        │
│  └────────────────────────────────────────────────────────────── │
│                                                                    │
│  Effective Permissions (Union of all roles): 1                    │
│  file_public                                                      │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  📋 All Roles in System                                           │
│                                                                    │
│  ▼ Role: Admin (6 permissions)                                   │
│     Assigned to: Carol                                            │
│     Permissions: db_admin, db_readonly, file_public, ...          │
│                                                                    │
│  ▼ Role: Developer (3 permissions)                               │
│     Assigned to: Alice                                            │
│     Permissions: db_readonly, file_public, service_user           │
│                                                                    │
│  [More roles...]                                                  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Status Colors:
- ✅ **Green** = Success, safe, permitted
- ⚠️ **Yellow/Orange** = Warning, high-privilege
- 🚨 **Red** = Error, security risk, escalation
- ℹ️ **Blue** = Information, neutral

### Node Colors in Graph:
- 🔵 **Light Blue** (#4C9BE8) = Users
- 🟢 **Green** (#66BB6A) = Normal resources
- 🟠 **Orange** (#FF9800) = High-privilege resources
- 🔴 **Red** (#E63946) = Escalation targets

### Edge Colors:
- **Gray** (#888888) = Normal permissions
- **Orange dashed** (#FFA726) = Vulnerabilities
- **Red thick** (#E63946) = Escalation paths

## Interactive Elements

### Buttons & Controls:
- **Dropdown** - User selection
- **Radio buttons** - Analysis type
- **Checkbox** - Attack scenario toggle
- **Expanders** - Collapsible details
- **Metrics** - Numerical displays

### Dynamic Content:
- Content changes based on selected user
- Graph updates with attack mode
- Natural language adapts to paths
- Colors change based on risk level

## Responsive Layout

The app uses Streamlit's column system:
- **3-column layout** for permission lists
- **2-column layout** for metrics
- **4-column layout** for statistics
- **Full width** for graphs and tables

## Accessibility Features

- **Clear hierarchy** with headers
- **Visual indicators** (icons, colors)
- **Explanatory text** for each section
- **Progressive disclosure** (expanders)
- **Consistent formatting** throughout

---

**This is what users will see when they launch the app!** 🎉

Clean, intuitive, and educational interface for exploring access control security.
