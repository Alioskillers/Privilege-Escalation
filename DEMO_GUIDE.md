# 🎯 Quick Demo Guide

Follow these steps to explore the Access Control Security Simulator:

## 🚀 Step 1: Launch the App

```bash
./run.sh
```

Or manually:
```bash
.venv/bin/streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📋 Step 2: Try These Scenarios

### Scenario A: View Basic Permissions
1. **Select user**: `bob` (sidebar)
2. **Analysis type**: `View Permissions`
3. **Observe**: Bob only has access to `file_public` and `service_user`

### Scenario B: Check Admin Privileges
1. **Select user**: `carol`
2. **Analysis type**: `View Permissions`
3. **Observe**: Carol has access to ALL resources (she's an admin)

### Scenario C: Detect Privilege Escalation (Safe)
1. **Select user**: `bob`
2. **Analysis type**: `Privilege Escalation`
3. **Attack mode**: OFF
4. **Observe**: ✅ No escalation detected (system is secure)

### Scenario D: Simulate Security Vulnerability 🚨
1. **Select user**: `bob`
2. **Toggle**: `Enable Attack Scenario` (sidebar)
3. **Analysis type**: `Privilege Escalation`
4. **Observe**: 
   - 🚨 Warning appears
   - Escalation paths are discovered
   - Natural language explanation shows the attack chain

### Scenario E: Visualize the Network
1. **Analysis type**: `Graph Visualization`
2. **With attack mode OFF**:
   - See clean permission structure
   - Blue = users, Green = resources
3. **With attack mode ON**:
   - See vulnerability paths (dashed orange)
   - Red arrows show escalation routes

### Scenario F: Explore RBAC
1. **Analysis type**: `RBAC Model`
2. **Select different users** to see their roles:
   - `carol` → admin (all permissions)
   - `alice` → developer
   - `bob` → guest (minimal access)
   - `dave` → analyst

---

## 🎓 Learning Objectives

### What You'll Understand:

1. **Direct vs. Indirect Access**
   - Direct: explicitly granted permissions
   - Indirect: access through chains/delegation

2. **Privilege Escalation**
   - How low-privilege users can reach high-value resources
   - Why even small misconfigurations are dangerous

3. **RBAC Benefits**
   - Simplifies permission management
   - Users inherit role permissions
   - Easier to audit and maintain

4. **Graph-Based Security Analysis**
   - Visualize complex permission relationships
   - Identify risky paths before attackers do

---

## 💡 Tips for Exploration

### Try These Experiments:

1. **Compare Users**
   - Switch between `bob` and `carol` in Privilege Escalation view
   - Notice how carol has legitimate access, bob doesn't

2. **Attack Mode Toggle**
   - Turn attack mode ON/OFF repeatedly
   - Watch the graph visualization change
   - See how one backdoor creates multiple escalation paths

3. **Examine the Paths**
   - In escalation results, expand each path
   - Read the natural language explanation
   - Follow the technical path step-by-step

4. **RBAC Comparison**
   - Look at RBAC model
   - See how roles map to the ACM (Access Control Matrix)
   - Notice how multiple users can share roles

---

## 🔍 What to Look For

### In Normal Mode (Secure):
- ✅ Low-privilege users (bob, dave, eve) cannot reach high-privilege resources
- Clear separation between roles
- No red warning messages

### In Attack Mode (Vulnerable):
- 🚨 Escalation paths appear
- Red arrows in graph
- Natural language shows the exploit chain
- Example: "Bob can access service_user, which connects to db_admin"

---

## 📊 Understanding the Data

### High-Privilege Resources (Protected):
- `file_secret` - Confidential documents
- `db_admin` - Database administrator access
- `service_root` - Root-level service control

### User Privilege Levels:
- **carol** (admin) - Full access ✓
- **alice** (developer) - Medium access
- **bob, eve** (guest) - Minimal access
- **dave** (analyst) - Read-only access

### Attack Scenario Simulation:
The attack mode adds:
- Hidden path: `service_user` → `db_admin`
- Backdoor: `file_public` → `file_secret`

This simulates common real-world vulnerabilities like:
- Misconfigured service accounts
- Overly permissive API endpoints
- Unintended delegation chains

---

## 🎯 Key Takeaways

1. **Principle of Least Privilege**: Give users only what they need
2. **Transitive Access Matters**: Not just direct permissions
3. **Graph Analysis is Powerful**: Visualize to understand
4. **One Misconfiguration = Big Problem**: Attack mode shows this
5. **RBAC Simplifies Management**: But still need to verify

---

## 🛠️ Next Steps

Want to customize?
1. Edit `data/sample_permissions.json`
2. Add your own users/resources
3. Define custom roles
4. Reload the app and explore!

---

## ❓ Troubleshooting

**App won't start?**
```bash
.venv/bin/pip install -r requirements.txt
```

**Import errors?**
```bash
cd "Privilage Esculation"
.venv/bin/python -c "from backend.matrix_model import AccessControlMatrix; print('OK')"
```

**Port already in use?**
```bash
.venv/bin/streamlit run app.py --server.port 8502
```

---

## 📚 Learn More

This tool demonstrates concepts from:
- Computer security textbooks
- Access control models (DAC, MAC, RBAC)
- Graph theory in security
- Privilege escalation techniques

Perfect for:
- Students learning security
- Demonstrating vulnerabilities
- Teaching access control
- Security awareness training

---

**Ready to explore?** Launch the app and start with Scenario D (Attack Mode) for maximum impact! 🚀
