# streamlit_banking_firestore.py
import os
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import matplotlib.pyplot as plt
import random
from pathlib import Path

st.set_page_config(page_title="Mini Banking App (Firestore)", layout="wide")

# ---------------- Firebase init ----------------
def init_firebase():
    """
    Initialize firebase-admin using inline key JSON (directly parsed in memory).
    No need to write/read from a file.
    """
    import json
    from firebase_admin import credentials, firestore
    import firebase_admin

    FIREBASE_KEY_JSON = """
{
  "type": "service_account",
  "project_id": "kudumbanidhihybrid1",
  "private_key_id": "106a3aea20284dd69f1423d5a503d3aaf3ca5bcd",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDKO/MMgTFi5NlH\\nZC8ouJ7P2qqnAnQaUH5bLZGABf3D5T98euHo+ia4CAdAHd3DTPvYbAsDVjs1Y7qn\\nO/NA2JrZmCPnk80C1TTm5njo8B2VclMG/HI67zhHuBGhNmlU62SrSrdJi+P5491k\\n8DHMXUnLNmm9pkSigxgWA/2bF7gMrnuvZi/FoX1X3SSOpJLwhmyD1cNrWpPgxxBQ\\n9R7GvrxhV5gmrNsWgpwlfGxYZsNW0TmhqFKu4q/bKHmqKsslPCXKdmwNf/Lb54fq\\nt6ri7H5ZoVJrHVDYv4oUgbgTdhvXZkVyyWOEuR7Wb/nuJxUEZ71Xh/3XoY86vOMj\\nkFMG6jT3AgMBAAECggEAUW5kRpO65BxMFUAU8Sut3voonwkQ4QuqZWJq5QcEkJ29\\nu4zrbFlVv+KTsNCV3C8idZnDsXtGahAXN4GfSGwvphBp3LSZ51scayFAbGNLNkML\\nhZOfF3X9znsitixnq2cBaSuzs+ydRqDnI97H3odt0GK/nzrVBi8NQsgmlQ2u8YOU\\n4t3cMtHPYdMpz5jeIqPZwxHfAEwU7tf4zd2bB6evHELQgu1OIT4D+QbakVDu2ZZf\\nn7UPDp0GY3P+8vm5WYPpZ8hcl53XGCR/1vXtGeSjhgEuciRRSQV01VZ0vi4b+yQ7\\nDGqp7AwRUprlXuWATPm9HJQ6HrnNcS5V5SS5yl02aQKBgQDzzDQAnvwtmnNPZsLF\\nleyvsxdDvszhSqMVxU3RLrG/YfPwI2SD+ltoc+NVczVNMQvA39Y/jLrotAqWEeVw\\n/dihVrB8Zo4gPlPv+Ibp6tpa/SHniIC4TG4axTd8Mr3jyf0JUF6AlCrzRJnUO5BS\\nOwzyJgfFf41Q5fR553eKeQdQNQKBgQDUWzC3/KFt2voPpUBXU5O/hdOn7AHMDWfc\\nLtSMtMm0TveoOo+LjttCpIDZvQuqLcDNsE28Xul6X9W4JO3WEAQ3JdjjZmPP+h5R\\ndDwadm3WdwD14M9CmAecjCu0O2pxwuLG66h5lGzJEZs+MdacbJLk0gKxIb6U+Jim\\n+h+4ZDht+wKBgEmSCOtbDtywLDX827AGkztePxoJfQhLnrVWKiqC/c60P4nrFE0j\\nguwddK/3qVEXCOX2ZlAdJtZMZpls4yFa6UGeyHlx9VfTlz7mb8gtQCGPG+kj7zwu\\njFd1xk2rflQ8QyjJYQtKKz/oJse+Bcpa2YhFY7j8yedszX7wE8nsxgE1AoGAU1yk\\n6GUM/fILXh7x/hX6FyIy72WPYwoULnRXzhCeaeDiCbFLbm6bFjM7vb4fmSOy30wJ\\niBv+LaL3Y/1jPDg3X2rFFKe6IQe/5RvrCDxba+h1gRBKbIr/2e2QroTwiU4G9i3G\\nikvA1MHLnoO0Ct34YEks81oa1aItUsc3sovtNwcCgYEAjNAeMOnOjHzJCAn5/R8J\\nuqvpor0IW5qvqtLGVj9bTU1KFIcGcf6KDAxhGcORxQ8RRr+6kV/aWVGPZ5cPZZ7D\\nh24wbZmKqBwg1WEQ0dlpFKo4Hk9eis5bOSf5FttsofZHEAEe9ZVGcAnBYs1EPeyc\\nYz3o0wrO7onVEnOY2irlXDs=\\n-----END PRIVATE KEY-----\\n",
  "client_email": "firebase-adminsdk-fbsvc@kudumbanidhihybrid1.iam.gserviceaccount.com",
  "client_id": "100226831792574113374",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40kudumbanidhihybrid1.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""


    # Load JSON string into Python dict
    key_dict = json.loads(FIREBASE_KEY_JSON)

    # Initialize Firebase only once
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()
db = init_firebase()

# ---------------- Authentication ----------------
def login(username, password):
    doc = db.collection("accounts").document(username).get()
    if not doc.exists:
        return None
    acc = doc.to_dict()
    if acc.get("password") == password:
        return acc
    return None

if "user" not in st.session_state:
    st.session_state.user = {"role": "guest"}

if st.session_state.user.get("role") != "admin":
    st.sidebar.info("🔓 Viewing as Guest (read-only)")
    with st.sidebar.form("login_form"):
        uname = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            acc = login(uname, pwd)
            if acc and acc.get("role") == "admin":
                st.session_state.user = acc
                st.experimental_rerun()
            else:
                st.error("Invalid credentials or not an admin")
else:
    st.sidebar.success(f"✅ Logged in as {st.session_state.user['username']} (Admin)")
    if st.sidebar.button("Logout"):
        st.session_state.user = {"role": "guest"}
        st.experimental_rerun()

def is_admin():
    return st.session_state.user.get("role") == "admin"

# ---------------- Helpers ----------------
def now():
    return datetime.utcnow().isoformat(sep=' ', timespec='seconds')

def get_rules():
    doc = db.collection("config").document("rules").get()
    if doc.exists:
        return doc.to_dict()
    else:
        defaults = {"deposit_interest_pct": 5.0, "loan_interest_pct": 10.0, "loan_capability_pct": 50.0}
        db.collection("config").document("rules").set(defaults)
        return defaults

def set_rules(rules):
    db.collection("config").document("rules").set(rules)

def next_id(prefix, collection_name):
    max_n = 0
    for d in db.collection(collection_name).stream():
        obj = d.to_dict()
        did = obj.get("id") or d.id
        if isinstance(did, str) and did.startswith(prefix + "_"):
            try:
                n = int(did.split("_")[-1])
                if n > max_n:
                    max_n = n
            except:
                pass
    return f"{prefix}_{max_n + 1}"

def get_all_users():
    users = []
    for d in db.collection("users").stream():
        u = d.to_dict()
        users.append({
            "id": u.get("id", d.id),
            "name": u.get("name", ""),
            "family": u.get("family", ""),
            "created_at": u.get("created_at", ""),
            "allow_deposit": u.get("allow_deposit", True),
            "balance": float(u.get("balance", 0.0))
        })
    users.sort(key=lambda x: x["id"])
    return users

def get_all_transactions():
    tx = []
    for d in db.collection("transactions").stream():
        tx.append(d.to_dict())
    tx.sort(key=lambda x: x.get("timestamp", ""), reverse=False)
    return tx

def get_all_loans():
    loans = []
    for d in db.collection("loans").stream():
        loans.append(d.to_dict())
    loans.sort(key=lambda x: x.get("created_at", ""), reverse=False)
    return loans

def find_user(user_id):
    doc = db.collection("users").document(user_id).get()
    return doc.to_dict() if doc.exists else None

# ---------------- Business logic ----------------
# (same as your previous code: create_user, add_deposit, freeze_user,
#  calculate_loan_capability, create_loan, add_interest_to_deposits,
#  add_loan_interest_to_deposit)

# ---------------- Utilities ----------------
def load_snapshot():
    return {
        "users": get_all_users(),
        "transactions": get_all_transactions(),
        "loans": get_all_loans(),
        "rules": get_rules()
    }

# ---------------- Streamlit UI ----------------
data = load_snapshot()

if is_admin():
    menu = st.sidebar.selectbox("Navigation", [
        "Dashboard", "Users", "Create User", "Manage Rules",
        "Deposits / Interest", "Loans", "Transactions",
        "Summary & Projections", "Seed Users"
    ])
else:
    menu = st.sidebar.selectbox("Navigation", [
        "Dashboard", "Users", "Transactions", "Summary & Projections"
    ])

# Example of protecting menus
if menu == "Create User":
    if not is_admin():
        st.warning("Admins only. Please login.")
    else:
        # your create user code here...
        pass

elif menu == "Manage Rules":
    if not is_admin():
        st.warning("Admins only. Please login.")
    else:
        # your manage rules code here...
        pass

elif menu == "Users":
    st.header("Users")
    users_df = pd.DataFrame(data["users"]) if data["users"] else pd.DataFrame()
    st.dataframe(users_df)
    if is_admin():
        st.subheader("Admin actions")
        # your deposit/freeze/interest logic here...

# (repeat same pattern for Deposits/Interest, Loans, Seed Users)

# Keep Dashboard, Transactions, Summary always visible (guest or admin)

st.sidebar.markdown("---")
st.sidebar.write("Firestore project connected")
