# streamlit_banking_firestore.py
import os
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
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


# db = init_firebase()

# ---------------- Firebase init ----------------
# def init_firebase():
#     """
#     Initialize firebase-admin using either:
#      - local file 'firebase_key.json'
#      - env var FIREBASE_KEY_PATH pointing to JSON file
#      - Streamlit secret 'firebase_key' (full JSON content) -> written to firebase_key.json at runtime
#     """
#     # 1) If Streamlit secrets contains JSON string under 'firebase_key', write to file
#     if st.secrets and "firebase_key" in st.secrets:
#         key_path = "firebase_key.json"
#         # write only if file doesn't exist or content differs
#         if not Path(key_path).exists():
#             with open(key_path, "w") as f:
#                 f.write(st.secrets["firebase_key"])
#     else:
#         # 2) environment variable
#         key_path = os.environ.get("FIREBASE_KEY_PATH", "firebase_key.json")

#     if not Path(key_path).exists():
#         st.error(
#             "Firebase service account key not found. Place your service account JSON at "
#             f"'{key_path}' or add it to Streamlit secrets as 'firebase_key'."
#         )
#         st.stop()

#     cred = credentials.Certificate(key_path)
#     # Avoid reinitialization
#     if not firebase_admin._apps:
#         firebase_admin.initialize_app(cred)
#     return firestore.client()

db = init_firebase()

# ---------------- Helpers ----------------
def now():
    return datetime.utcnow().isoformat(sep=' ', timespec='seconds')

def get_rules():
    doc = db.collection("config").document("rules").get()
    if doc.exists:
        return doc.to_dict()
    else:
        defaults = {
            "deposit_interest_pct": 5.0,
            "loan_interest_pct": 10.0,
            "loan_capability_pct": 50.0
        }
        db.collection("config").document("rules").set(defaults)
        return defaults

def set_rules(rules):
    db.collection("config").document("rules").set(rules)

def next_id(prefix, collection_name):
    # build next id like prefix_1, prefix_2 ...
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
        # ensure keys exist
        users.append({
            "id": u.get("id", d.id),
            "name": u.get("name", ""),
            "family": u.get("family", ""),
            "created_at": u.get("created_at", ""),
            "allow_deposit": u.get("allow_deposit", True),
            "balance": float(u.get("balance", 0.0))
        })
    # maintain same ordering as before (optional)
    users.sort(key=lambda x: x["id"])
    return users

def get_all_transactions():
    tx = []
    for d in db.collection("transactions").stream():
        t = d.to_dict()
        tx.append(t)
    tx.sort(key=lambda x: x.get("timestamp", ""), reverse=False)
    return tx

def get_all_loans():
    loans = []
    for d in db.collection("loans").stream():
        l = d.to_dict()
        loans.append(l)
    loans.sort(key=lambda x: x.get("created_at", ""), reverse=False)
    return loans

def find_user(user_id):
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return None
    return doc.to_dict()

# ---------------- Business logic (Firestore-backed) ----------------

def create_user(name, family, initial_deposit, allow_deposit=True):
    uid = next_id("user", "users")
    user = {
        "id": uid,
        "name": name,
        "family": family,
        "created_at": now(),
        "allow_deposit": bool(allow_deposit),
        "balance": float(initial_deposit)
    }
    # create user document with id = uid
    db.collection("users").document(uid).set(user)
    # create initial transaction
    tid = next_id("txn", "transactions")
    txn = {
        "id": tid,
        "user_id": uid,
        "type": "deposit",
        "amount": float(initial_deposit),
        "note": "Initial deposit",
        "timestamp": now()
    }
    db.collection("transactions").document(tid).set(txn)
    return user

def add_deposit(user_id, amount, note=""):
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return False, "User not found"
    user = user_doc.to_dict()
    if not user.get("allow_deposit", True):
        return False, "Depositing is disabled for this account"
    amt = float(amount)
    new_balance = float(user.get("balance", 0.0)) + amt
    # use a batch to update user and create txn
    tid = next_id("txn", "transactions")
    txn = {
        "id": tid,
        "user_id": user_id,
        "type": "deposit",
        "amount": amt,
        "note": note,
        "timestamp": now()
    }
    batch = db.batch()
    batch.update(user_ref, {"balance": new_balance})
    batch.set(db.collection("transactions").document(tid), txn)
    batch.commit()
    return True, txn

def freeze_user(user_id, freeze=True):
    user_ref = db.collection("users").document(user_id)
    if not user_ref.get().exists:
        return False
    user_ref.update({"allow_deposit": not bool(freeze)})
    return True

def calculate_loan_capability(user_id):
    user = find_user(user_id)
    if not user:
        return 0.0
    pct = get_rules().get("loan_capability_pct", 50.0) / 100.0
    return float(user.get("balance", 0.0)) * pct

def create_loan(user_id, amount, note=""):
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return False, "User not found"
    user = user_doc.to_dict()
    capability = calculate_loan_capability(user_id)
    if amount > capability:
        return False, f"Amount exceeds loan capability: {capability:.2f}"
    lid = next_id("loan", "loans")
    loan = {
        "id": lid,
        "user_id": user_id,
        "principal": float(amount),
        "created_at": now(),
        "note": note,
        "interest_paid_to_deposit": 0.0
    }
    # batch: create loan doc + update user balance + create txn
    tid = next_id("txn", "transactions")
    txn = {
        "id": tid,
        "user_id": user_id,
        "type": "loan_disbursed",
        "amount": float(amount),
        "note": f"Loan disbursed: {note}",
        "timestamp": now()
    }
    new_balance = float(user.get("balance", 0.0)) + float(amount)
    batch = db.batch()
    batch.set(db.collection("loans").document(lid), loan)
    batch.update(user_ref, {"balance": new_balance})
    batch.set(db.collection("transactions").document(tid), txn)
    batch.commit()
    return True, loan

def add_interest_to_deposits(amount_per_user=None, user_id=None, note=""):
    rules = get_rules()
    rule_pct = rules.get("deposit_interest_pct", 5.0)
    added = []
    if user_id:
        u_ref = db.collection("users").document(user_id)
        u_doc = u_ref.get()
        if not u_doc.exists:
            return []
        u = u_doc.to_dict()
        if amount_per_user is not None:
            amt = float(amount_per_user)
        else:
            amt = float(u.get("balance", 0.0)) * (rule_pct / 100.0)
        new_balance = float(u.get("balance", 0.0)) + amt
        tid = next_id("txn", "transactions")
        txn = {"id": tid, "user_id": user_id, "type": "interest", "amount": amt, "note": note, "timestamp": now()}
        batch = db.batch()
        batch.update(u_ref, {"balance": new_balance})
        batch.set(db.collection("transactions").document(tid), txn)
        batch.commit()
        added.append(txn)
    else:
        # apply to all users (process in batches if many)
        users = list(db.collection("users").stream())
        for doc in users:
            u = doc.to_dict()
            uid = u.get("id", doc.id)
            if amount_per_user is not None:
                amt = float(amount_per_user)
            else:
                amt = float(u.get("balance", 0.0)) * (rule_pct / 100.0)
            new_balance = float(u.get("balance", 0.0)) + amt
            tid = next_id("txn", "transactions")
            txn = {"id": tid, "user_id": uid, "type": "interest", "amount": amt, "note": note, "timestamp": now()}
            batch = db.batch()
            batch.update(db.collection("users").document(uid), {"balance": new_balance})
            batch.set(db.collection("transactions").document(tid), txn)
            batch.commit()
            added.append(txn)
    return added

def add_loan_interest_to_deposit(loan_id, note=""):
    loan_ref = db.collection("loans").document(loan_id)
    loan_doc = loan_ref.get()
    if not loan_doc.exists:
        return False, "Loan not found"
    loan = loan_doc.to_dict()
    pct = get_rules().get("loan_interest_pct", 10.0)
    interest = float(loan.get("principal", 0.0)) * (pct / 100.0)
    user_id = loan.get("user_id")
    # batch update loan and user + create txn
    tid = next_id("txn", "transactions")
    txn = {"id": tid, "user_id": user_id, "type": "loan_interest_credit", "amount": interest, "note": note or "Loan interest credited", "timestamp": now()}
    batch = db.batch()
    # update loan's interest_paid_to_deposit
    current_paid = float(loan.get("interest_paid_to_deposit", 0.0))
    batch.update(loan_ref, {"interest_paid_to_deposit": current_paid + interest})
    # update user balance
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return False, "User for loan not found"
    user = user_doc.to_dict()
    new_balance = float(user.get("balance", 0.0)) + interest
    batch.update(user_ref, {"balance": new_balance})
    batch.set(db.collection("transactions").document(tid), txn)
    batch.commit()
    return True, interest

# ---------------- Utilities ----------------
def load_snapshot():
    # Returns a dict similar to your old JSON 'data'
    data = {
        "users": get_all_users(),
        "transactions": get_all_transactions(),
        "loans": get_all_loans(),
        "rules": get_rules()
    }
    return data

def generate_sample_users(n=20):
    families = ["Sharma", "Patel", "Iyer", "Das", "Rao"]
    for i in range(1, n + 1):
        name = f"User{i}"
        family = random.choice(families)
        deposit = random.randint(500, 5000)
        create_user(name, family, deposit, allow_deposit=True)
        # Randomly assign loan (~50%)
        if random.choice([True, False]):
            # compute user id created above
            uid = next_id("user", "users")  # careful: next_id returns next available (we need previous created id)
            # Instead get last created user by scanning users
            users = get_all_users()
            if users:
                last = users[-1]  # recently inserted last by id ordering
                loan_amt = random.randint(1000, 4000)
                create_loan(last["id"], loan_amt, note="Sample loan")

# ---------------------- Streamlit UI ----------------------
data = load_snapshot()

menu = st.sidebar.selectbox("Navigation", [
    "Dashboard",
    "Users",
    "Create User",
    "Manage Rules",
    "Deposits / Interest",
    "Loans",
    "Transactions",
    "Summary & Projections",
    "Seed Users"
])

# Dashboard
if menu == "Dashboard":
    st.header("Overview")
    users_df = pd.DataFrame(data["users"])
    st.metric("Total users", len(users_df))
    total_deposits = users_df["balance"].sum() if not users_df.empty else 0.0
    total_loans = sum(l.get("principal", 0.0) for l in data["loans"]) if data.get("loans") else 0.0
    st.metric("Total deposits (balance)", f"{total_deposits:.2f}")
    st.metric("Total loans (principal)", f"{total_loans:.2f}")
    st.subheader("Rules")
    st.write(data["rules"])

# Create User
elif menu == "Create User":
    st.header("Create New User")
    with st.form("create_user"):
        name = st.text_input("Full name")
        family = st.text_input("Family name / Group")
        init_deposit = st.number_input("Initial deposit", min_value=0.0, value=0.0, step=100.0)
        allow_deposit = st.checkbox("Allow further deposits?", value=True)
        submitted = st.form_submit_button("Create")
        if submitted:
            if not name:
                st.error("Name is required")
            else:
                create_user(name, family, init_deposit, allow_deposit)
                st.success("User created")
                st.rerun()

# Users
elif menu == "Users":
    st.header("Users")
    users_df = pd.DataFrame(data["users"]) if data["users"] else pd.DataFrame(columns=["id", "name", "family", "balance", "allow_deposit"])
    st.dataframe(users_df)
    if st.button("Generate 20 Sample Users"):
        for _ in range(20):
            name = f"User{random.randint(1000,9999)}"
            family = random.choice(["Sharma","Patel","Iyer","Das","Rao"])
            deposit = random.randint(500,5000)
            create_user(name,family,deposit)
        st.success("20 sample users added")
        st.rerun()

    st.subheader("Select a user to view details")
    user_ids = [u["id"] for u in data["users"]]
    selected = st.selectbox("User", ["-- select --"] + user_ids)
    if selected and selected != "-- select --":
        u = find_user(selected)
        st.write(u)
        st.markdown("**Transactions**")
        txns = [t for t in data["transactions"] if t.get("user_id") == selected]
        txns_df = pd.DataFrame(txns)
        st.dataframe(txns_df)

        st.markdown("**Actions**")
        col1, col2, col3 = st.columns(3)
        with col1:
            amt = st.number_input("Deposit amount", min_value=0.0, value=0.0, key="dep_amt")
            note = st.text_input("Note", key="dep_note")
            if st.button("Add deposit", key="add_dep"):
                ok, res = add_deposit(selected, amt, note)
                if ok:
                    st.success("Deposit added")
                    st.rerun()
                else:
                    st.error(res)
        with col2:
            freeze = st.checkbox("Freeze account (stop depositing)", value=not u.get("allow_deposit", True), key="freeze")
            if st.button("Apply freeze", key="apply_freeze"):
                freeze_user(selected, freeze)
                st.success("Freeze status updated")
                st.rerun()
        with col3:
            st.markdown("**Add interest to this user**")
            one_amt = st.checkbox("Use fixed amount instead of pct?", key="one_amt_chk")
            if one_amt:
                fixed = st.number_input("Fixed amount", min_value=0.0, value=0.0, key="fixed_interest")
                if st.button("Add fixed interest", key="add_fixed_interest"):
                    added = add_interest_to_deposits(amount_per_user=fixed, user_id=selected, note="Manual interest added")
                    st.success(f"Added interest: {fixed:.2f}")
                    st.rerun()
            else:
                if st.button("Add interest by rule (pct)", key="add_pct_interest"):
                    added = add_interest_to_deposits(user_id=selected, note="Interest by rule")
                    st.success("Interest added based on rule")
                    st.rerun()

# Manage Rules
elif menu == "Manage Rules":
    st.header("Global Rules & Percentages")
    rules = data.get("rules", {})
    with st.form("rules_form"):
        dep_pct = st.number_input("Deposit interest % (annual)", value=float(rules.get("deposit_interest_pct", 5.0)), step=0.1)
        loan_pct = st.number_input("Loan interest % (annual)", value=float(rules.get("loan_interest_pct", 10.0)), step=0.1)
        loan_cap = st.number_input("Loan capability % of balance", value=float(rules.get("loan_capability_pct", 50.0)), step=1.0)
        submitted = st.form_submit_button("Save rules")
        if submitted:
            new_rules = {
                "deposit_interest_pct": float(dep_pct),
                "loan_interest_pct": float(loan_pct),
                "loan_capability_pct": float(loan_cap)
            }
            set_rules(new_rules)
            st.success("Rules updated")
            st.rerun()

# Deposits / Interest
elif menu == "Deposits / Interest":
    st.header("Apply Interest / Bulk Operations")
    st.write("Current deposit interest pct (annual):", data["rules"]["deposit_interest_pct"])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add interest to all by rule (pct)"):
            added = add_interest_to_deposits(note="Interest added to all by rule")
            st.success(f"Interest added to {len(added)} users")
            st.rerun()
    with col2:
        fixed_amt = st.number_input("Add fixed amount to everyone (per user)", min_value=0.0, value=0.0)
        if st.button("Add fixed amount to everyone"):
            added = add_interest_to_deposits(amount_per_user=fixed_amt, note="Fixed amount added to all")
            st.success(f"Added fixed amount to {len(added)} users")
            st.rerun()

# Loans
elif menu == "Loans":
    st.header("Loans")
    st.subheader("Create loan for user")
    user_ids = [u["id"] for u in data["users"]]
    loan_user = st.selectbox("User", ["--select--"] + user_ids)
    loan_amount = st.number_input("Amount", min_value=0.0, value=0.0)
    loan_note = st.text_input("Note")
    if st.button("Create loan"):
        if loan_user == "--select--":
            st.error("Select user")
        else:
            ok, res = create_loan(loan_user, loan_amount, loan_note)
            if ok:
                st.success("Loan created and disbursed")
                st.rerun()
            else:
                st.error(res)

    st.subheader("Loans list")
    loans_df = pd.DataFrame(data.get("loans", []))
    st.dataframe(loans_df)

    st.subheader("Add loan interest to deposit (for a loan)")
    loan_ids = [l["id"] for l in data.get("loans", [])]
    sel_loan = st.selectbox("Loan", ["--select--"] + loan_ids)
    if st.button("Add loan interest to deposit"):
        if sel_loan == "--select--":
            st.error("Select loan")
        else:
            ok, res = add_loan_interest_to_deposit(sel_loan, note="Loan interest credited to deposit")
            if ok:
                st.success(f"Interest amount {res:.2f} added to user's deposit")
                st.rerun()
            else:
                st.error(res)

# Transactions
elif menu == "Transactions":
    st.header("All Transactions")
    txns_df = pd.DataFrame(data.get("transactions", []))
    st.dataframe(txns_df)

# Summary & Projections
elif menu == "Summary & Projections":
    st.header("Summaries")
    users_df = pd.DataFrame(data["users"]).fillna(0) if data["users"] else pd.DataFrame(columns=["id", "name", "family", "balance"])
    st.subheader("Member-wise summary")
    st.dataframe(users_df[["id", "name", "family", "balance"]])

    st.subheader("Family-wise summary")
    if not users_df.empty:
        fam = users_df.groupby("family")["balance"].agg(["sum", "count"]).reset_index()
        fam = fam.rename(columns={"sum": "total_balance", "count": "members"})
        st.dataframe(fam)

    st.subheader("Charts")
    if not users_df.empty:
        fig, ax = plt.subplots()
        ax.bar(users_df["name"].tolist(), users_df["balance"].tolist())
        ax.set_title("Balance per member")
        ax.set_xlabel("Member")
        ax.set_ylabel("Balance")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    st.subheader("Projection Tool")
    st.write("Simple projection using current deposit interest % (annual) compounded yearly")
    years = st.slider("Years to project", min_value=1, max_value=30, value=5)
    rate = data["rules"].get("deposit_interest_pct", 5.0) / 100.0
    proj = []
    if not users_df.empty:
        for _, row in users_df.iterrows():
            start = row["balance"]
            vals = [start * ((1 + rate) ** y) for y in range(0, years+1)]
            proj.append({"id": row["id"], "name": row["name"], **{f"y_{y}": vals[y] for y in range(0, years+1)}})
        proj_df = pd.DataFrame(proj)
        st.dataframe(proj_df)
        totals = [proj_df[f"y_{y}"].sum() for y in range(0, years+1)]
        fig2, ax2 = plt.subplots()
        ax2.plot(list(range(0, years+1)), totals)
        ax2.set_title("Total deposits projection")
        ax2.set_xlabel("Years")
        ax2.set_ylabel("Total balance")
        st.pyplot(fig2)

st.sidebar.markdown("---")
st.sidebar.write("Firestore project: (read from your service account)")
st.sidebar.write("Collections: users, transactions, loans, config (rules)")

# End of file