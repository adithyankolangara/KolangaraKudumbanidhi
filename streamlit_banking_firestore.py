import streamlit as st
import pandas as pd
from firebase_admin import credentials, firestore
from datetime import datetime, UTC
from pathlib import Path
# from db1 import init_firebase
import urllib.parse

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="കൊളങ്ങര കുടുംബനിധി ", layout="wide")
# st.dataframe(df, use_container_width=True)
# st.bar_chart(df, use_container_width=True)
st.markdown("""
<style>
/* Make text scale on small screens */
html, body, [class*="css"]  {
    font-size: 16px;
}

/* Ensure input boxes take full width */
.stTextInput, .stSelectbox, .stButton button {
    width: 100% !important;
}

/* Reduce padding on mobile */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)
# ---------------- Hide Streamlit Default UI ----------------
import streamlit as st

# ---------------- Hide Streamlit Branding Completely ----------------
hide_streamlit_style = """
    <style>
    /* Hide Streamlit's default header, footer, and menus */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hide Deploy/Manage App button */
    .stAppDeployButton {display: none !important;}
    .stActionButton {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .viewerBadge_link__1S137 {display: none !important;}

    /* Hide Streamlit bottom-right toolbar (including Manage app) */
    .css-164nlkn.egzxvld1 {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------- Firebase Init ----------------
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

# ---------------- Automatic DB Bootstrap ----------------
def bootstrap_db():
    rules_ref = db.collection("config").document("rules")
    if not rules_ref.get().exists:
        rules_ref.set({
            "deposit_interest_pct": 5.0,
            "loan_interest_pct": 10.0,
            "loan_capability_pct": 50.0
        })

    admin_ref = db.collection("accounts").document("admin")
    if not admin_ref.get().exists:
        admin_ref.set({
            "username": "admin",
            "password": "admin123",   # ⚠️ change in production!
            "role": "admin",
            "created_at": datetime.now(UTC).isoformat()
        })

bootstrap_db()

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
    with st.sidebar.form("login_form"):
        uname = st.text_input("Username", key="login_username")
        pwd = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")
        if submitted:
            acc = login(uname, pwd)
            if acc and acc.get("role") == "admin":
                st.session_state.user = acc
                st.rerun()
            else:
                st.error("Invalid credentials or not an admin")
else:
    st.sidebar.success(f"✅ Logged in as {st.session_state.user['username']} (Admin)")
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.user = {"role": "guest"}
        st.rerun()
def display_dashboard():
    st.title("📊 Mini Banking Analytics Dashboard")

    families = get_all_families()

    # ---------------- Family-wise Deposits ----------------
    st.subheader("Family-wise Deposits / Withdrawals / Balance")
    family_summary = []
    for fam in families:
        total_dep = get_total_deposits(family_name=fam)
        total_with = get_total_withdrawals(family_name=fam)
        balance = get_balance(family_name=fam)
        family_summary.append({
            "Family": fam,
            "Total Deposits": total_dep,
            "Total Withdrawals": total_with,
            "Balance": balance
        })
    st.dataframe(pd.DataFrame(family_summary).sort_values("Family"))

    # ---------------- User-wise Deposits ----------------
    st.subheader("User-wise Deposits / Withdrawals / Balance")
    user_summary = []
    for fam in families:
        users = get_users_by_family(fam)
        for u in users:
            total_dep = get_total_deposits(user_id=u["user_id"])
            total_with = get_total_withdrawals(user_id=u["user_id"])
            balance = get_balance(user_id=u["user_id"])
            user_summary.append({
                "Family": fam,
                "User": u["first_name"],
                "User ID": u["user_id"],
                "Total Deposits": total_dep,
                "Total Withdrawals": total_with,
                "Balance": balance
            })
    st.dataframe(pd.DataFrame(user_summary).sort_values(["Family", "User"]))

    # ---------------- Global Totals ----------------
    st.subheader("Global Totals")
    st.markdown(f"**Total Deposits:** {get_total_deposits()}")
    st.markdown(f"**Total Withdrawals:** {get_total_withdrawals()}")
    st.markdown(f"**Overall Balance:** {get_balance()}")

    # ---------------- Loan Statistics ----------------
    # ---------------- Loan Statistics ----------------
    st.subheader("Active Loans per Family")
    loan_summary_family = []
    loan_summary_user = []

    for fam in families:
        fam_loans = get_family_loans(fam)
        loan_summary_family.append({
            "Family": fam,
            "Active Loans": len(fam_loans),
            "Total Loan Amount": sum(l["principal_amount"] for l in fam_loans),
            "Total Remaining Amount": sum(l["remaining_amount"] for l in fam_loans)
        })

        users = get_users_by_family(fam)
        for u in users:
            user_loans = get_user_loans(u["user_id"])
            for l in user_loans:
                paid_emi_count = int(l['paid_amount'] // l['emi_amount'])
                remaining_emi_count = int(max(0, (l['total_loan_amount'] - l['paid_amount']) // l['emi_amount']))
                loan_summary_user.append({
                    "Family": fam,
                    "User": u["first_name"],
                    "User ID": u["user_id"],
                    "Loan ID": l["loan_id"],
                    "Principal": l["principal_amount"],
                    "Total Loan Amount": l["total_loan_amount"],
                    "Remaining Amount": l["remaining_amount"],
                    "EMI Amount": l["emi_amount"],
                    "Tenure Months": l["tenure_months"],
                    "Status": l["status"],
                    "Paid EMIs": paid_emi_count,
                    "Remaining EMIs": remaining_emi_count
                })

    st.markdown("#### Family Level Loan Summary")
    st.dataframe(pd.DataFrame(loan_summary_family).sort_values("Family"))

    st.markdown("#### User Level Loan Details")
    st.dataframe(pd.DataFrame(loan_summary_user).sort_values(["Family", "User"]))

def is_admin():
    
    return st.session_state.user.get("role") == "admin"

# ---------------- User Management ----------------
def get_all_families():
    users = db.collection("users").stream()
    families = sorted(set([u.to_dict().get("family_name", "") for u in users if u.to_dict().get("family_name")]))
    return families

def get_next_user_id(family_name):
    users = db.collection("users").where("family_name", "==", family_name).stream()
    numbers = []
    for u in users:
        uid = u.to_dict().get("user_id", "")
        if uid.startswith(family_name + "-"):
            try:
                num = int(uid.split("-")[-1])
                numbers.append(num)
            except:
                pass
    next_num = max(numbers) + 1 if numbers else 1
    return f"{family_name}-{next_num}"

def add_user(first_name, family_name, mobile_number=None):
    user_id = get_next_user_id(family_name)
    ref = db.collection("users").document(user_id)
    if ref.get().exists:
        st.error("⚠️ User ID already exists (unexpected conflict)")
    else:
        ref.set({
            "user_id": user_id,
            "first_name": first_name,
            "family_name": family_name,
            "mobile_number": mobile_number,
            "status": "active",
            "created_at": datetime.now(UTC).isoformat()
        })
        st.success(f"✅ User {first_name} created with ID {user_id}!")

def update_user(user_id, first_name=None, family_name=None, status=None, mobile_number=None):
    ref = db.collection("users").document(user_id)
    if not ref.get().exists:
        st.error("⚠️ User not found")
    else:
        updates = {}
        if first_name:
            updates["first_name"] = first_name
        if family_name:
            updates["family_name"] = family_name
        if status:
            updates["status"] = status
        if mobile_number:
            updates["mobile_number"] = mobile_number
        if updates:
            ref.update(updates)
            st.success(f"✅ User {user_id} updated successfully!")

def get_user(user_id):
    ref = db.collection("users").document(user_id).get()
    return ref.to_dict() if ref.exists else None

def get_users_by_family(family_name):
    users = db.collection("users").where("family_name", "==", family_name).stream()
    return [u.to_dict() for u in users]

def move_user(user_id, new_family):
    ref = db.collection("users").document(user_id)
    doc = ref.get()
    if not doc.exists:
        st.error("⚠️ User not found")
        return
    user = doc.to_dict()
    new_user_id = get_next_user_id(new_family)
    db.collection("users").document(new_user_id).set({
        **user,
        "user_id": new_user_id,
        "family_name": new_family,
        "moved_from": user.get("family_name"),
        "moved_at": datetime.now(UTC).isoformat()
    })
    ref.delete()
    st.success(f"✅ User moved from {user['family_name']} to {new_family} (New ID: {new_user_id})")
    
    # Send WhatsApp notification
    send_whatsapp_action(user, "user_moved", new_family=new_family, new_user_id=new_user_id)

def remove_user(user_id):
    ref = db.collection("users").document(user_id)
    doc = ref.get()
    if not doc.exists:
        st.error("⚠️ User not found")
        return
    user = doc.to_dict()
    db.collection("removed_users").document(user_id).set({
        **user,
        "removed_at": datetime.now(UTC).isoformat()
    })
    ref.delete()
    st.success(f"🗑️ User {user_id} removed and archived.")
    
    # Send WhatsApp notification
    send_whatsapp_action(user, "user_updated", status="removed")

def remove_family(family_name):
    users = get_users_by_family(family_name)
    if not users:
        st.warning("⚠️ No users found for this family")
        return
    batch = db.batch()
    for u in users:
        user_ref = db.collection("users").document(u["user_id"])
        removed_ref = db.collection("removed_users").document(u["user_id"])
        batch.set(removed_ref, {**u, "removed_at": datetime.now(UTC).isoformat()})
        batch.delete(user_ref)
        # Send WhatsApp for each user
        send_whatsapp_action(u, "user_updated", status="removed")
    batch.commit()
    st.success(f"🗑️ Family '{family_name}' and {len(users)} users removed & archived.")

# ---------------- WhatsApp Helper ----------------
def send_whatsapp(to_number, message):
    digits = "".join(filter(str.isdigit, to_number))
    if digits.startswith("0"):
        digits = digits[1:]
    encoded_message = urllib.parse.quote(message)
    wa_url = f"https://wa.me/{digits}?text={encoded_message}"
    st.markdown(f"[💬 Send WhatsApp Message]({wa_url})", unsafe_allow_html=True)

def send_whatsapp_action(user, action_type, **kwargs):
    """
    Send a WhatsApp message for a given action.
    action_type: deposit, withdrawal, user_created, user_updated, user_moved, loan_granted, loan_repaid
    kwargs: action-specific details
    """
    if not user.get("mobile_number"):
        return
    
    msg = f"Hi {user.get('first_name')},\n"
    
    if action_type == "deposit":
        msg += f"കൊളങ്ങര  കുടുംബ നിധിയിൽ  {kwargs.get('amount')} രൂപയുടെ നിക്ഷേപം  {kwargs.get('date')} നു കിട്ടി.\n"
        msg += f"മുൻപിലത്തെ ബാലൻസ് : {kwargs.get('prev_balance')} രൂപ\nഇപ്പോളത്തെ  ബാലൻസ് : {kwargs.get('new_balance')} രൂപ\n"
        if kwargs.get("remarks"):
            msg += f"📝 Remarks: {kwargs.get('remarks')}"
            
    elif action_type == "withdrawal":
        msg += f"💸 കൊളങ്ങര  കുടുംബ നിധിയിൽ നിന്ന് {kwargs.get('amount')} രൂപ {kwargs.get('date')} നു  പിൻവലിച്ചു.\n"
        msg += f"മുൻപിലത്തെ ബാലൻസ് : {kwargs.get('prev_balance')} രൂപ\nഇപ്പോളത്തെ  ബാലൻസ് :{kwargs.get('new_balance')} രൂപ\n"
        if kwargs.get("remarks"):
            msg += f"📝 Remarks: {kwargs.get('remarks')}"
            
    elif action_type == "user_created":
        msg += f"✅ നമസ്കാരം കൊളങ്ങര  കുടുംബ നിധിയിൽ - {kwargs.get('family_name')} ഉപതാവഴിയുടെ കീഴിൽ  അംഗത്വം  തുടങ്ങിയിരിക്കുന്നു ഇൽ \n. Your User ID: {kwargs.get('user_id')}."
        
    elif action_type == "user_updated":
        msg += "📝 നമസ്കാരം കൊളങ്ങര  കുടുംബ നിധിയിൽ താങ്കളുടെ  വ്യക്തിഗത വിവരങ്ങൾ അപ്ഡേറ്റ്  ചെയ്തിരിക്കുന്നു :\n"
        for k,v in kwargs.items():
            msg += f"{k}: {v}\n"
            
    elif action_type == "user_moved":
        msg += f"നമസ്കാരം കൊളങ്ങര  കുടുംബ നിധിയിൽ {kwargs.get('new_family')} ഉപതാവഴിയുടെ കീഴിലേക്ക്  മാറ്റിയിരിക്കുന്നു . New User ID: {kwargs.get('new_user_id')}."
        
    elif action_type == "loan_granted":
        msg += f"🏦 നമസ്കാരം കൊളങ്ങര  കുടുംബ നിധിയിൽനിന്ന് താങ്കൾക്ക്: {kwargs.get('amount')}രൂപ  ലോൺ  അനുവദിച്ചിരിക്കുന്നു \n, ആകെ തിരിച്ചടവ് - പലിശയും  ചേർത്ത് (പലിശ സംഘ്യ ലോൺ ഗഡുക്കൾ തീരുന്ന മുറക്ക്  വ്യക്തിഗത  അക്കൗന്റിലേക്ക് നിക്ഷേപമായി  ചേർക്കുന്നതാണ് : {kwargs.get('total')}\nതവണ സംഖ്യ: {kwargs.get('emi')}, കാലാവധി: {kwargs.get('tenure')} മാസം."
        
    elif action_type == "loan_repaid":
        msg += f"💳 Loan Payment of {kwargs.get('amount')} received on {kwargs.get('date')}.\n"
        msg += f"ആകെ  {kwargs.get('total_emis')} തവണകളിൽ {kwargs.get('paid_emis')}) അടച്ചു\n"
        msg += f"ഇനി  {kwargs.get('remaining')} രൂപ  തിരിച്ചു അടക്കാനുണ്ട് "
        if kwargs.get('remarks'):
            msg += f"\n📝 Remarks: {kwargs.get('remarks')}"
        if kwargs.get('interest'):
            msg += f"\nInterest Credited: {kwargs.get('interest')}"
    
    elif action_type == "loan_completed":
        msg += "🎉 Congratulations! Your loan has been fully repaid.\n"
        msg += f"ആകെ: {kwargs.get('total_paid')} രൂപ  തിരിച്ചടച്ചിരിക്കുന്നു \n"
        msg += f"{kwargs.get('total_emis')} തവണ\n"
        msg += f"പൂർത്തിയാക്കിയ  തിയ്യതി : {kwargs.get('date')}"

    elif action_type == "summary":
        # Summary message
        msg += f"📊 Account Summary:\n"
        msg += f"Total Deposits: {kwargs.get('deposit')}\n"
        msg += f"Total Withdrawals: {kwargs.get('withdrawal')}\n"
        
        loans = kwargs.get("loans", [])
        if loans:
            msg += "\n💳 Loan Details:\n"
            for l in loans:
                msg += (
                    f"- Loan {l['loan_id']}:\n"
                    f"  തവണ: {l['paid_emis']}/{l['total_emis']}\n"
                    f"  അടച്ച തുക : : {l['paid_amount']}\n"
                    f"  ബാക്കി അടക്കാനുള്ളത് :: {l['remaining_amount']}\n"
                )
        else:
            msg += "\n✅  നിലവിൽ ലോണുകൾ ഒന്നും ഇല്ല്യ."
    
    send_whatsapp(user.get("mobile_number"), msg)

# ---------------- Transactions ----------------
# ---------------- Transactions ----------------
def add_deposit(user_id, amount, date, remarks=None):
    user = get_user(user_id)
    if not user:
        st.error("⚠️ User not found")
        return None, None
    
    prev_balance = get_balance(user_id)
    
    # Save transaction in DB
    tx_ref = db.collection("transactions").document()
    tx_ref.set({
        "user_id": user_id,
        "family_name": user.get("family_name"),
        "amount": amount,
        "type": "deposit",
        "date": date.isoformat(),
        "remarks": remarks or "",
        "created_at": datetime.now(UTC).isoformat()
    })
    
    new_balance = get_balance(user_id)
    st.success(f"✅ Deposit of {amount} added for {user_id} ({user.get('first_name')}) on {date}")
    
    # Send WhatsApp
    # if user.get("mobile_number"):
    #     msg = (
    #         f"💰 Deposit Alert\n"
    #         f"User: {user['first_name']}\n"
    #         f"Date: {date}\n"
    #         f"Previous Balance: {prev_balance}\n"
    #         f"Deposited Amount: {amount}\n"
    #         f"Current Balance: {new_balance}"
    #     )
    #     if remarks and remarks.strip():
    #         msg += f"\n📝 Remarks: {remarks}"
    #     send_whatsapp(user["mobile_number"], msg)
    
    return prev_balance, new_balance

def add_withdrawal(user_id, amount, date, remarks=None):
    user = get_user(user_id)
    if not user:
        st.error("⚠️ User not found")
        return None, None
    
    prev_balance = get_balance(user_id)
    if amount > prev_balance:
        st.error(f"⚠️ Insufficient balance. Available: {prev_balance}")
        return None, None

    # Save transaction in DB
    tx_ref = db.collection("transactions").document()
    tx_ref.set({
        "user_id": user_id,
        "family_name": user.get("family_name"),
        "amount": amount,
        "type": "withdrawal",
        "date": date.isoformat(),
        "remarks": remarks or "",
        "created_at": datetime.now(UTC).isoformat()
    })
    
    new_balance = get_balance(user_id)
    st.success(f"✅ Withdrawal of {amount} recorded for {user_id} ({user.get('first_name')}) on {date}")
    
    # Send WhatsApp
    # if user.get("mobile_number"):
    #     msg = (
    #         f"💸 Withdrawal Alert\n"
    #         f"User: {user['first_name']}\n"
    #         f"Date: {date}\n"
    #         f"Previous Balance: {prev_balance}\n"
    #         f"Withdrawn Amount: {amount}\n"
    #         f"Current Balance: {new_balance}"
    #     )
    #     if remarks and remarks.strip():
    #         msg += f"\n📝 Remarks: {remarks}"
    #     send_whatsapp(user["mobile_number"], msg)
    
    return prev_balance, new_balance

def get_transactions(user_id=None, family_name=None):
    ref = db.collection("transactions")
    if user_id:
        ref = ref.where("user_id", "==", user_id)
    if family_name:
        ref = ref.where("family_name", "==", family_name)
    return [tx.to_dict() for tx in ref.stream()]

def get_total_deposits(user_id=None, family_name=None):
    txs = get_transactions(user_id, family_name)
    return sum(tx["amount"] for tx in txs if tx.get("type")=="deposit")

def get_total_withdrawals(user_id=None, family_name=None):
    txs = get_transactions(user_id, family_name)
    return sum(tx["amount"] for tx in txs if tx.get("type")=="withdrawal")

def get_balance(user_id=None, family_name=None):
    return get_total_deposits(user_id, family_name) - get_total_withdrawals(user_id, family_name)

# ---------------- Loan Rules ----------------
def get_loan_rules():
    doc = db.collection("config").document("loan_rules").get()
    if not doc.exists:
        # default rules
        db.collection("config").document("loan_rules").set({
            "family_max_loans": 3,
            "user_max_loans": 1,
            "interest_pct": 10.0,
            "deposit_pct_for_loan": 50.0
        })
        doc = db.collection("config").document("loan_rules").get()
    return doc.to_dict()

def get_family_loans(family_name):
    return [l.to_dict() for l in db.collection("loans").where("family_name", "==", family_name).where("status", "==", "active").stream()]

def get_user_loans(user_id):
    return [l.to_dict() for l in db.collection("loans").where("user_id", "==", user_id).where("status", "==", "active").stream()]

def calculate_emi(principal, interest_rate, tenure_months):
    """
    Flat EMI calculation: EMI = (Loan Amount + Total Interest) / Total EMIs
    """
    total_interest = principal * (interest_rate / 100)
    total_payable = principal + total_interest
    emi = total_payable / tenure_months
    return round(emi, 2)

def max_loan_amount(user_id, family_name):
    """
    Max loan is based on family's total deposits × deposit_pct_for_loan,
    minus all active loans already taken by that family.
    """
    rules = get_loan_rules()
    # total deposits at family level
    family_total_dep = get_total_deposits(family_name=family_name)
    # all active family loans (sum of principals)
    family_existing_loans = sum(l["principal_amount"] for l in get_family_loans(family_name))
    # maximum allowed based on rules
    max_family_amount = (family_total_dep * rules["deposit_pct_for_loan"] / 100) - family_existing_loans

    return max(0, max_family_amount)


# ---------------- Admin Dashboard ----------------
if is_admin():
    st.title("👨‍💼 Admin Dashboard")
    menu = st.sidebar.radio("Menu", [
        "User Management",
        "Add Deposit",
        "Add Withdrawal",
        "Transaction History / Totals",
        "Deposit Summary",
        "Send WhatsApp Summary","Repay Loan","Loan Management","Rules / Config","Dashboard / Stats"], key="admin_sidebar_menu")

    # ---------------- Transaction History / Totals ----------------
    if menu == "Transaction History / Totals":
        st.subheader("Transaction History / Totals")
        families = get_all_families()
        selected_family = st.selectbox("Select Family (Optional)", ["All"] + families, key="txn_family_select")
        family_name = selected_family if selected_family != "All" else None
        txns = get_transactions(family_name=family_name)
        if txns:
            df = pd.DataFrame(txns)
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["balance_after_txn"] = df.apply(lambda x: get_balance(user_id=x["user_id"]), axis=1)
            st.dataframe(df.sort_values("date", ascending=False))
            st.markdown(f"**Total Deposits:** {get_total_deposits(family_name=family_name)}")
            st.markdown(f"**Total Withdrawals:** {get_total_withdrawals(family_name=family_name)}")
            st.markdown(f"**Current Balance:** {get_balance(family_name=family_name)}")
        else:
            st.info("No transactions found.")

    # ---------------- Deposit Summary ----------------
    elif menu == "Deposit Summary":
        st.subheader("Deposit Summary per Family/User")
        families = get_all_families()
        selected_family = st.selectbox("Select Family", ["All"] + families, key="summary_family_select")
        if selected_family == "All":
            summary = []
            for fam in families:
                total_dep = get_total_deposits(family_name=fam)
                total_with = get_total_withdrawals(family_name=fam)
                balance = get_balance(family_name=fam)
                summary.append({
                    "Family": fam,
                    "Total Deposits": total_dep,
                    "Total Withdrawals": total_with,
                    "Balance": balance
                })
            st.dataframe(pd.DataFrame(summary))
        else:
            users = get_users_by_family(selected_family)
            summary = []
            for u in users:
                total_dep = get_total_deposits(user_id=u["user_id"])
                total_with = get_total_withdrawals(user_id=u["user_id"])
                balance = get_balance(user_id=u["user_id"])
                summary.append({
                    "User": u["first_name"],
                    "Total Deposits": total_dep,
                    "Total Withdrawals": total_with,
                    "Balance": balance
                })
            st.dataframe(pd.DataFrame(summary))

    # ---------------- Add Deposit / Withdrawal / User Management ----------------

    # ---------------- User Management ----------------
    elif menu == "User Management":
        st.subheader("User Management")
        user_tab = st.radio("Choose Option", ["➕ Add User", "✏️ Update User", "👀 View Users", "🔀 Move User", "🗑️ Remove User/Family"], key="user_mgmt_tab")

        # ➕ Add User
        if user_tab == "➕ Add User":
            families = get_all_families()
            family_mode = st.radio("Family Option", ["Select Existing Family", "Create New Family"], key="family_mode_add")
            if family_mode == "Select Existing Family" and families:
                family_name = st.selectbox("Choose Family", families, key="select_family_add")
            else:
                family_name = st.text_input("Enter New Family Name", key="new_family_add")
            first_name = st.text_input("First Name", key="first_name_add")
            mobile_number = st.text_input("Mobile Number", key="mobile_number_add")
            if family_name:
                suggested_user_id = get_next_user_id(family_name)
                st.info(f"Next User ID will be: **{suggested_user_id}**")
            if st.button("Add User", key="add_user_button"):
                if first_name and family_name:
                    user_id = get_next_user_id(family_name)
                    add_user(first_name, family_name, mobile_number)
                    user = get_user(user_id)  # fetch newly created user
                    send_whatsapp_action(user, "user_created", family_name=family_name, user_id=user_id)
                else:
                    st.error("⚠️ Family Name and First Name are required")
                # ✏️ Update User
        elif user_tab == "✏️ Update User":
            with st.form("update_user_form"):
                user_id = st.text_input("User ID to Update (e.g., Smith-2)", key="update_user_id")
                new_first = st.text_input("New First Name (leave blank if no change)", key="update_first_name")
                new_family = st.text_input("New Family Name (leave blank if no change)", key="update_family_name")
                new_status = st.selectbox("Status", ["", "active", "frozen"], key="update_status")
                new_mobile = st.text_input("New Mobile Number (leave blank if no change)", key="update_mobile")
                submitted = st.form_submit_button("Update User")
                if submitted:
                    if user_id:
                        update_user(user_id, new_first or None, new_family or None, new_status or None, new_mobile or None)
                        user = get_user(user_id)
                        send_whatsapp_action(user, "user_updated", first_name=new_first, family=new_family, status=new_status, mobile=new_mobile)
                    else:
                        st.error("⚠️ User ID required")

        # 👀 View Users
        elif user_tab == "👀 View Users":
            view_option = st.radio("Choose View", ["Individual", "Family"], key="view_option")
            if view_option == "Individual":
                all_users = [u.to_dict() for u in db.collection("users").stream()]
                user_options = [f"{u['first_name']} ({u['user_id']})" for u in all_users]
                selected_user_str = st.selectbox("Select User", [""] + user_options, key="view_individual_select")
                if st.button("Fetch User", key="fetch_individual_button"):
                    if selected_user_str:
                        uid = selected_user_str.split("(")[-1].replace(")","")
                        user = get_user(uid)
                        if user:
                            st.json(user)
                        else:
                            st.warning("No user found")
                    else:
                        st.warning("Select a user")
            elif view_option == "Family":
                families = get_all_families()
                if families:
                    fam = st.selectbox("Select Family", families, key="view_family_select")
                    if st.button("Fetch Family", key="fetch_family_button"):
                        users = get_users_by_family(fam)
                        if users:
                            st.dataframe(pd.DataFrame(users))
                        else:
                            st.warning("No users found for this family")
                else:
                    st.info("No families available yet.")

        # 🔀 Move User
        elif user_tab == "🔀 Move User":
            move_user_id = st.text_input("Enter User ID to Move", key="move_user_id")
            families = get_all_families()
            new_family = st.selectbox("Move to Family", families + ["Create New"], key="move_select_family")
            if new_family == "Create New":
                new_family = st.text_input("Enter New Family Name", key="move_new_family_name")
            if st.button("Move User", key="move_user_button"):
                if move_user_id and new_family:
                    move_user(move_user_id, new_family)

                else:
                    st.error("⚠️ Provide User ID and Family Name")

        # 🗑️ Remove User/Family
        elif user_tab == "🗑️ Remove User/Family":
            remove_mode = st.radio("Remove", ["User", "Family"], key="remove_mode")
            if remove_mode == "User":
                uid_remove = st.text_input("Enter User ID to Remove", key="remove_user_id")
                if st.button("Remove User", key="remove_user_button"):
                    if uid_remove:
                        remove_user(uid_remove)
                    else:
                        st.error("⚠️ User ID required")
            elif remove_mode == "Family":
                families = get_all_families()
                fam_remove = st.selectbox("Select Family to Remove", families, key="remove_family_select")
                if st.button("Remove Family", key="remove_family_button"):
                    if fam_remove:
                        remove_family(fam_remove)
                    else:
                        st.error("⚠️ Family required")

# ---------------- Add Deposit ----------------
    elif menu == "Add Deposit":
        st.subheader("Add Deposit for User")
        families = get_all_families()
        if families:
            selected_family = st.selectbox("Select Family", families, key="deposit_family_select")
            users_in_family = get_users_by_family(selected_family)
            if users_in_family:
                user_options = [f"{u['first_name']} ({u['user_id']})" for u in users_in_family]
                selected_user_str = st.selectbox("Select User", user_options, key="deposit_user_select")
                deposit_user_id = selected_user_str.split("(")[-1].replace(")", "")
                
                # Show current balance and total deposits
                current_balance = get_balance(user_id=deposit_user_id)
                total_deposits = get_total_deposits(user_id=deposit_user_id)
                st.info(f"💰 Current Balance: {current_balance} | Total Deposits so far: {total_deposits}")
                
            else:
                st.warning("No users found in this family.")
                deposit_user_id = None
        else:
            st.info("No families available.")
            deposit_user_id = None

        deposit_amount = st.number_input("Deposit Amount", min_value=0.0, step=1.0, key="deposit_amount")
        deposit_date = st.date_input("Deposit Date", value=datetime.now().date(), key="deposit_date")
        deposit_remarks = st.text_input("Remarks / Comments", key="deposit_remarks")

        if st.button("Add Deposit", key="deposit_button"):
            if deposit_user_id and deposit_amount > 0:
                prev_balance, new_balance = add_deposit(deposit_user_id, deposit_amount, deposit_date, deposit_remarks)
                if prev_balance is not None:
                    user = get_user(deposit_user_id)
                    total_deposits = get_total_deposits(user_id=deposit_user_id)

                    # ✅ Use centralized WhatsApp action
                    send_whatsapp_action(
                        user,
                        "deposit",
                        amount=deposit_amount,
                        date=deposit_date,
                        prev_balance=prev_balance,
                        new_balance=new_balance,
                        total_deposits=total_deposits,
                        remarks=deposit_remarks
                    )

                    st.success(f"✅ Deposit of {deposit_amount} recorded and WhatsApp notification prepared.")


    # ---------------- Add Withdrawal ----------------
    elif menu == "Add Withdrawal":
        st.subheader("Record Withdrawal for User")
        families = get_all_families()
        if families:
            selected_family = st.selectbox("Select Family", families, key="withdraw_family_select")
            users_in_family = get_users_by_family(selected_family)
            if users_in_family:
                user_options = [f"{u['first_name']} ({u['user_id']})" for u in users_in_family]
                selected_user_str = st.selectbox("Select User", user_options, key="withdraw_user_select")
                withdraw_user_id = selected_user_str.split("(")[-1].replace(")", "")
            else:
                st.warning("No users found in this family.")
                withdraw_user_id = None
        else:
            st.info("No families available.")
            withdraw_user_id = None

        withdraw_amount = st.number_input("Withdrawal Amount", min_value=0.0, step=1.0, key="withdraw_amount")
        withdraw_date = st.date_input("Withdrawal Date", value=datetime.now().date(), key="withdraw_date")
        withdraw_remarks = st.text_input("Remarks / Comments", key="withdraw_remarks")  # <-- Add this

        if st.button("Record Withdrawal", key="withdraw_button"):
            if withdraw_user_id and withdraw_amount > 0:
                # data_remarks = st.text_input("Enter Remarks (Optional)", key="withdraw_remarks")
                
                prev_balance, new_balance = add_withdrawal(withdraw_user_id, withdraw_amount, withdraw_date, remarks=withdraw_remarks)
                
                if prev_balance is not None:
                    user = get_user(withdraw_user_id)
                    # Use send_whatsapp_action instead of manually formatting the message
                    send_whatsapp_action(
                        user, 
                        action_type="withdrawal",
                        amount=withdraw_amount,
                        date=withdraw_date,
                        prev_balance=prev_balance,
                        new_balance=new_balance,
                        remarks=withdraw_remarks
                    )
            else:
                st.error("⚠️ Provide valid User and Amount")

    elif menu == "Send WhatsApp Summary":
        st.subheader("📲 Send WhatsApp Summary to a User")

        families = get_all_families()
        selected_family = st.selectbox("Select Family", families, key="wa_family_select")

        users_to_notify = get_users_by_family(selected_family) if selected_family else []
        user_names = {u["first_name"]: u for u in users_to_notify}

        selected_user_name = st.selectbox("Select User", list(user_names.keys()), key="wa_user_select")
        selected_user = user_names.get(selected_user_name)

        if selected_user:
            deposit_total = get_total_deposits(user_id=selected_user["user_id"])
            withdrawal_total = get_total_withdrawals(user_id=selected_user["user_id"])

            from firebase_admin import firestore

            def get_user_loan_summary(user_id: str) -> dict:
                """
                Fetch loan summary for a given user_id.
                Returns dict with paid_emi, pending_emi, balance.
                """
                db = firestore.client()
                loans_ref = db.collection("loans").where("user_id", "==", user_id)
                docs = loans_ref.stream()

                loan_summary = {
                    "paid_emi": 0,
                    "pending_emi": 0,
                    "balance": 0
                }

                for doc in docs:
                    loan = doc.to_dict()
                    tenure = loan.get("tenure", 0)
                    emi = loan.get("emi", 0)
                    paid_emi = loan.get("paid_emi", 0)
                    balance = loan.get("balance", 0)

                    # If multiple loans, we accumulate
                    loan_summary["paid_emi"] += paid_emi
                    loan_summary["pending_emi"] += max(tenure - paid_emi, 0)
                    loan_summary["balance"] += balance if balance else max((tenure - paid_emi) * emi, 0)

                return loan_summary

            loan_info = get_user_loan_summary(selected_user["user_id"])  # <-- you need to implement this
            paid_emi = loan_info.get("paid_emi", 0)
            pending_emi = loan_info.get("pending_emi", 0)
            balance_amount = loan_info.get("balance", 0)

            message_template = st.text_area(
                "WhatsApp Message Template",
                value=(
                    "Hi {name},\n\n"
                    "💰 Total Deposit: {deposit}\n"
                    "💸 Total Withdrawal: {withdrawal}\n\n"
                    "🏦 Loan Summary:\n"
                    "✅ Paid EMI: {paid_emi}\n"
                    "⌛ Pending EMI: {pending_emi}\n"
                    "📉 Balance Amount: {balance}\n"
                ),
                height=180
            )

            if st.button("Send WhatsApp Message", key="wa_send_button"):
                msg = message_template.format(
                    name=selected_user.get("first_name"),
                    deposit=deposit_total,
                    withdrawal=withdrawal_total,
                    paid_emi=paid_emi,
                    pending_emi=pending_emi,
                    balance=balance_amount,
                )

                send_whatsapp_action(
                    selected_user,
                    action_type="summary",
                    msg=msg,
                    deposit=deposit_total,
                    withdrawal=withdrawal_total,
                    paid_emi=paid_emi,
                    pending_emi=pending_emi,
                    balance=balance_amount,
                )
                st.success(f"✅ WhatsApp message sent to {selected_user.get('first_name')}")

    elif menu == "Loan Management":
        st.subheader("Loan Management")
        rules = get_loan_rules()
        
        # Step 1: Choose Family
        families = get_all_families()
        selected_family = st.selectbox("Select Family", families, key="loan_family_select")
        family_loans = get_family_loans(selected_family)
        st.markdown(f"**Active Loans in Family:** {len(family_loans)} / Max Allowed: {rules['family_max_loans']}")
        
        # Step 2: Choose Member
        users_in_family = get_users_by_family(selected_family)
        user_options = [f"{u['first_name']} ({u['user_id']})" for u in users_in_family]
        selected_user_str = st.selectbox("Select User", user_options, key="loan_user_select")
        loan_user_id = selected_user_str.split("(")[-1].replace(")","")
        user_loans = get_user_loans(loan_user_id)
        st.markdown(f"**Active Loans for User:** {len(user_loans)} / Max Allowed: {rules['user_max_loans']}")
        user_total_deposit = get_total_deposits(user_id=loan_user_id)
        st.markdown(f"**Total Deposits:** {user_total_deposit}")
        max_loan = max_loan_amount(loan_user_id, selected_family)
        st.markdown(f"**Eligible Loan Amount:** {max_loan}")
        
        # Step 3: New Loan Input
        new_loan_amount = st.number_input("Loan Amount", min_value=0.0, max_value=max_loan, step=100.0, key="loan_amount")
        tenure_months = st.number_input("Tenure (months)", min_value=1, step=1, key="loan_tenure")
        
        if st.button("Proceed with Loan", key="proceed_loan_button"):
            if len(family_loans) >= rules["family_max_loans"]:
                st.error("Family has reached max concurrent loans")
            elif len(user_loans) >= rules["user_max_loans"]:
                st.error("User has reached max concurrent loans")
            elif new_loan_amount <= 0:
                st.error("Enter a valid loan amount")
            else:
                interest_pct = rules["interest_pct"]
                total_amount = round(new_loan_amount * (1 + interest_pct / 100), 2)
                emi_amount = calculate_emi(new_loan_amount, interest_pct, tenure_months)
                loan_ref = db.collection("loans").document()
                loan_ref.set({
                    "loan_id": loan_ref.id,
                    "user_id": loan_user_id,
                    "family_name": selected_family,
                    "principal_amount": new_loan_amount,
                    "total_loan_amount": total_amount,
                    "interest_rate": interest_pct,
                    "tenure_months": tenure_months,
                    "emi_amount": emi_amount,
                    "paid_amount": 0.0,
                    "remaining_amount": total_amount,
                    "start_date": datetime.now().isoformat(),
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                })
                st.success(f"✅ Loan Granted! Total Loan Amount: {total_amount}, EMI: {emi_amount}")
                
                # Send WhatsApp using action function
                user = get_user(loan_user_id)
                send_whatsapp_action(
                    user,
                    "loan_granted",
                    amount=new_loan_amount,
                    total=total_amount,
                    emi=emi_amount,
                    tenure=tenure_months
                )
        elif menu == "Rules / Config":
            st.subheader("Configure Rules")

            # ---------------- Fetch existing rules ----------------
            rules_doc = db.collection("config").document("rules").get()
            rules = rules_doc.to_dict() if rules_doc.exists else {}

            loan_rules_doc = db.collection("config").document("loan_rules").get()
            loan_rules = loan_rules_doc.to_dict() if loan_rules_doc.exists else {}

            st.markdown("### Deposit / General Rules")
            deposit_interest = st.number_input(
                "Deposit Interest (%)", 
                value=rules.get("deposit_interest_pct", 5.0), step=0.1
            )
            loan_capability = st.number_input(
                "Loan Capability (%)", 
                value=rules.get("loan_capability_pct", 50.0), step=1.0
            )

            st.markdown("### Loan Rules")
            family_max_loans = st.number_input(
                "Max Loans per Family", 
                value=loan_rules.get("family_max_loans", 3), min_value=1, step=1
            )
            user_max_loans = st.number_input(
                "Max Loans per User", 
                value=loan_rules.get("user_max_loans", 1), min_value=1, step=1
            )
            loan_interest = st.number_input(
                "Loan Interest Rate (%)", 
                value=loan_rules.get("interest_pct", 10.0), step=0.1
            )
            deposit_pct_for_loan = st.number_input(
                "Deposit % Used for Loan Eligibility", 
                value=loan_rules.get("deposit_pct_for_loan", 50.0), step=1.0
            )

            # ---------------- Live Loan Summary ----------------
            st.markdown("### Current Active Loans")

            families = get_all_families()
            if families:
                family_summary = []
                loan_summary = []

                for fam in families:
                    fam_loans = get_family_loans(fam)
                    total_active_loans_family = len(fam_loans)
                    family_summary.append({
                        "Family": fam,
                        "Active Loans": total_active_loans_family,
                        "Max Allowed": family_max_loans
                    })

                    users = get_users_by_family(fam)
                    for u in users:
                        user_loans = get_user_loans(u["user_id"])
                        loan_summary.append({
                            "Family": fam,
                            "User": u["first_name"],
                            "User ID": u["user_id"],
                            "Active Loans": len(user_loans),
                            "Max Allowed": user_max_loans
                        })

                st.markdown("#### Family Level Summary")
                st.dataframe(pd.DataFrame(family_summary).sort_values("Family"))

                st.markdown("#### User Level Breakdown")
                st.dataframe(pd.DataFrame(loan_summary).sort_values(["Family", "User"]))

            else:
                st.info("No families found.")

            # ---------------- Update Rules Button ----------------
            if st.button("Update Rules"):
                # Update general rules
                db.collection("config").document("rules").set({
                    "deposit_interest_pct": deposit_interest,
                    "loan_capability_pct": loan_capability
                })
                # Update loan rules
                db.collection("config").document("loan_rules").set({
                    "family_max_loans": family_max_loans,
                    "user_max_loans": user_max_loans,
                    "interest_pct": loan_interest,
                    "deposit_pct_for_loan": deposit_pct_for_loan
                })
                st.success("✅ Rules updated successfully")
        
    elif menu == "Repay Loan":
        st.subheader("Repay Loan")
        families = get_all_families()
        selected_family = st.selectbox("Select Family", families, key="repay_family")
        users_in_family = get_users_by_family(selected_family)
        user_options = [f"{u['first_name']} ({u['user_id']})" for u in users_in_family]
        selected_user_str = st.selectbox("Select User", user_options, key="repay_user")
        loan_user_id = selected_user_str.split("(")[-1].replace(")","")
        loans = get_user_loans(loan_user_id)
        
        if loans:
            loan_options = [f"{l['loan_id']} | Remaining: {l['remaining_amount']}" for l in loans]
            selected_loan_str = st.selectbox("Select Loan", loan_options, key="select_loan")
            loan_id = selected_loan_str.split("|")[0].strip()
            loan_doc = db.collection("loans").document(loan_id)
            loan = loan_doc.get().to_dict()
            
            st.markdown(f"**EMI Amount:** {loan['emi_amount']}, **Remaining Amount:** {loan['remaining_amount']}")
            # Calculate paid EMIs and remaining EMIs
            paid_emi_count = int(loan['paid_amount'] // loan['emi_amount'])
            total_emis = loan["tenure_months"]
            remaining_emi_count = total_emis - paid_emi_count
            st.markdown(f"**Paid EMIs:** {paid_emi_count}, **Remaining EMIs:** {remaining_emi_count}")

            pay_amount = st.number_input("Payment Amount", min_value=0.0, max_value=loan['remaining_amount'], step=1.0)
            remarks = st.text_input("Payment Remarks", value="Loan EMI payment")

        if st.button("Make Payment", key="repay_button"):
            payment_date = datetime.now().date().isoformat()
            
            # Update loan amounts
            loan['paid_amount'] += pay_amount
            loan['remaining_amount'] -= pay_amount

            # Log the payment history inside loan doc
            if "payments" not in loan:
                loan["payments"] = []
            loan["payments"].append({
                "amount": pay_amount,
                "date": payment_date,
                "remarks": remarks
            })

            # Recalculate EMI status
            paid_emi_count = int(loan['paid_amount'] // loan['emi_amount'])
            total_emis = loan["tenure_months"]
            remaining_emi_count = total_emis - paid_emi_count

            loan_completed = False

            # Check if this is the last payment
            if loan['remaining_amount'] <= 0:
                excess = abs(loan['remaining_amount'])
                loan['remaining_amount'] = 0
                loan['status'] = "completed"
                loan_completed = True

                # Deposit excess if any
                if excess > 0:
                    add_deposit(loan_user_id, excess, datetime.now().date(), remarks="Excess payment returned")

            # Save updates to Firestore
            loan_doc.update(loan)

            # Send WhatsApp notification
            user = get_user(loan_user_id)
            if loan_completed:
                send_whatsapp_action(
                    user,
                    "loan_completed",
                    total_paid=loan['paid_amount'],
                    total_emis=total_emis,
                    date=payment_date
                )
                st.success("🎉 Loan fully repaid! Completion notification sent.")
            else:
                send_whatsapp_action(
                    user,
                    "loan_repaid",
                    amount=pay_amount,
                    remaining=loan['remaining_amount'],
                    date=payment_date,
                    paid_emis=paid_emi_count,
                    total_emis=total_emis,
                    remarks=remarks
                )
                st.success(f"✅ Payment of {pay_amount} recorded and WhatsApp notification prepared.")
    
    elif menu == "Dashboard / Stats":
        display_dashboard()





