# 🔐 Access Control Security Simulator

An interactive web application for visualizing and analyzing access control security in computer systems.

## 🎯 Features

- **Permission Viewer**: See what resources each user can access
- **Privilege Escalation Detection**: Identify security vulnerabilities
- **Interactive Graph Visualization**: Visual representation of permission networks
- **RBAC Model Explorer**: Understand role-based access control
- **Attack Simulation**: Enable "attack mode" to demonstrate vulnerabilities

## 📦 Installation

1. **Ensure Python 3.8+ is installed**

2. **Install dependencies**:
```bash
cd "Privilage Esculation"
.venv/bin/pip install streamlit numpy networkx matplotlib
```

Or create a fresh virtual environment:
```bash
python3 -m venv .venv
.venv/bin/pip install streamlit numpy networkx matplotlib
```

## 🚀 Running the App

**Start the Streamlit app**:
```bash
.venv/bin/streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
project_root/
├── app.py                      # Main Streamlit application
├── backend/
│   ├── __init__.py
│   ├── matrix_model.py         # Access Control Matrix logic
│   ├── privilege_analysis.py   # Privilege escalation detection
│   ├── rbac.py                 # Role-Based Access Control
│   └── utils.py                # Visualization utilities
├── data/
│   └── sample_permissions.json # Permission configuration
└── README.md
```

## 🎮 How to Use

### 1. Select a User
Use the sidebar dropdown to choose which user to analyze (e.g., alice, bob, carol, dave, eve)

### 2. Choose Analysis Type
- **View Permissions**: See direct and reachable resources
- **Privilege Escalation**: Check for security vulnerabilities
- **Graph Visualization**: See the permission network
- **RBAC Model**: Explore role assignments

### 3. Enable Attack Scenario (Optional)
Toggle "Enable Attack Scenario" to inject vulnerabilities and see how privilege escalation works

## 🔍 Understanding the Results

### Permission Colors
- 🟢 **Green**: Normal resources
- 🟠 **Orange**: High-privilege resources
- 🔴 **Red**: Security risk (escalation detected)

### Graph Elements
- 🔵 **Blue nodes**: Users
- 🟢 **Green nodes**: Normal resources
- 🟠 **Orange nodes**: High-privilege resources
- 🔴 **Red arrows**: Escalation paths
- 🟠 **Dashed orange**: Vulnerability paths (attack mode)

## 📊 Sample Data

The app comes with sample data including:
- **5 users**: alice, bob, carol, dave, eve
- **6 resources**: file_secret, file_public, db_admin, db_readonly, service_root, service_user
- **4 roles**: admin, developer, analyst, guest

### High-Privilege Resources
- `file_secret`: Confidential files
- `db_admin`: Database admin access
- `service_root`: Root service access

## 🚨 Attack Scenario

When enabled, the attack scenario simulates:
- Hidden paths from `service_user` → `db_admin`
- Backdoor access from `file_public` → `file_secret`

This demonstrates how misconfigurations can lead to privilege escalation.

## 🔧 Customization

### Adding New Users/Resources

Edit `data/sample_permissions.json`:

```json
{
  "users": ["alice", "bob", "newuser"],
  "resources": ["file1", "file2", "newresource"],
  "permissions": {
    "alice": [1, 0, 1],
    "bob": [0, 1, 0],
    "newuser": [1, 1, 1]
  }
}
```

### Defining RBAC Roles

Add roles in the JSON:

```json
{
  "rbac": {
    "roles": {
      "myrole": ["resource1", "resource2"]
    },
    "user_roles": {
      "alice": ["myrole"]
    }
  }
}
```

## 🛠️ Technical Details

### Backend Components

1. **matrix_model.py**
   - Access Control Matrix (ACM) representation
   - Boolean matrix algebra
   - Transitive closure computation (Warshall's algorithm)

2. **privilege_analysis.py**
   - NetworkX graph construction
   - Path detection algorithms
   - Delegation edge management

3. **rbac.py**
   - Role definitions
   - User-role mappings
   - ACM derivation from RBAC

4. **utils.py**
   - Graph visualization with matplotlib
   - Pretty-printing utilities

### Technologies Used
- **Streamlit**: Web UI framework
- **NumPy**: Matrix operations
- **NetworkX**: Graph algorithms
- **Matplotlib**: Visualization

## 📝 License

This is an educational tool for demonstrating access control concepts.

## 🤝 Contributing

Feel free to extend the functionality:
- Add more analysis types
- Implement additional attack scenarios
- Enhance visualizations
- Add export features

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Use it to understand access control vulnerabilities and security best practices. Do not use on production systems without proper authorization.
