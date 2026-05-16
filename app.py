import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Initialize Application Page Configuration for mobile-friendly viewports
st.set_page_config(page_title="ACCO BOO Pro", layout="wide", initial_sidebar_state="collapsed")

# Inject global CSS for a smooth, high-performance mobile UI feel
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
    .stMetric {background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef;}
    div[data-testid="stHorizontalBlock"] {gap: 1rem;}
    </style>
""", unsafe_allowed_html=True)

# ==========================================
# 1. CLIENT BOOK REGISTRY
# ==========================================
CLIENTS_DATABASE = {
    "Client Alpha": {
        "entity_type": "Sole Trader (Individual)",
        "fy_start": "2026-01-01", "fy_end": "2026-12-31", "vat_due": "2026-05-20", 
        "default_vat": 0.23, "email": "alpha_tax@gmail.com", "allow_client_view": True
    },
    "Client Beta": {
        "entity_type": "Limited Company (Corporate)",
        "fy_start": "2026-04-01", "fy_end": "2027-03-31", "vat_due": "2026-06-15", 
        "default_vat": 0.135, "email": "beta_corp@gmail.com", "allow_client_view": True
    }
}

# ==========================================
# 2. SECURE AUTHENTICATION ENGINE
# ==========================================
if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = None
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

def render_login():
    st.sidebar.title("🔐 ACCO BOO Access Control")
    user = st.sidebar.text_input("Username / Client ID")
    pwd = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Authenticate", use_container_width=True):
        if user == "admin" and pwd == "acco_boo_master_2026":
            st.session_state['auth_status'] = "Admin"
            st.session_state['current_user'] = "Admin"
        elif user in CLIENTS_DATABASE and pwd == "password123":
            if CLIENTS_DATABASE[user]["allow_client_view"]:
                st.session_state['auth_status'] = "Client"
                st.session_state['current_user'] = user
            else:
                st.sidebar.error("❌ Portal Access Locked.")
        else:
            st.sidebar.error("❌ Invalid Credentials.")

render_login()

if st.session_state['auth_status'] is None:
    st.warning("🔒 Access Denied. Please open the sidebar and authenticate to initialize ACCO BOO.")
    st.stop()

# Multi-Book Routing
if st.session_state['auth_status'] == "Admin":
    active_client = st.sidebar.selectbox("📂 Select Active Client Book", list(CLIENTS_DATABASE.keys()))
else:
    active_client = st.session_state['current_user']
    st.sidebar.info(f"Connected Book: {active_client}")

client_meta = CLIENTS_DATABASE[active_client]

# ==========================================
# 3. APPLICATION FRAMEWORK & DASHBOARD
# ==========================================
st.title(f"📊 {active_client} Portal")
st.caption(f"Entity Classification: **{client_meta['entity_type']}**")

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Financial Year Ends", client_meta["fy_end"])
with m2:
    vat_date_obj = datetime.strptime(client_meta["vat_due"], "%Y-%m-%d").date()
    days_to_vat = (vat_date_obj - datetime.today().date()).days
    st.metric("VAT Deadline", client_meta["vat_due"], f"{days_to_vat} Days Rem.", delta_color="inverse")
with m3:
    st.metric("System Mode", st.session_state['auth_status'])

# ==========================================
# 4. INTEGRATED TAX COMPUTATION ENGINES
# ==========================================
st.header("🧮 Tax Calculation Matrix")

net_taxable_profit = st.number_input("Adjusted Net Taxable Profit (€)", min_value=0.00, value=55000.00, step=1000.00)

if client_meta["entity_type"] == "Sole Trader (Individual)":
    st.subheader("👤 Individual Income Tax Estimator")
    
    col_status, col_credits = st.columns(2)
    with col_status:
        filing_status = st.selectbox("Filing Status Structure", ["Single Filer", "Married (One Income)", "Married (Two Incomes)"])
    with col_credits:
        tax_credits = st.number_input("Annual Personal Tax Credits (€)", min_value=0.00, value=4000.00, step=100.00)
    
    if filing_status == "Single Filer":
        srcop = 44000.00
    elif filing_status == "Married (One Income)":
        srcop = 53000.00
    else:
        srcop = 88000.00
        
    if net_taxable_profit <= srcop:
        tax_at_20 = net_taxable_profit * 0.20
        tax_at_40 = 0.00
    else:
        tax_at_20 = srcop * 0.20
        tax_at_40 = (net_taxable_profit - srcop) * 0.40
        
    gross_income_tax = tax_at_20 + tax_at_40
    net_income_tax_due = max(0.00, gross_income_tax - tax_credits)
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.info(f"**Standard Band (20%):** €{tax_at_20:,.2f}\n\n**Higher Band (40%):** €{tax_at_40:,.2f}")
    with t_col2:
        st.metric("Net Income Tax Liability", f"€{net_income_tax_due:,.2f}")

else:
    st.subheader("🏢 Corporate Tax Liability Engine")
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        passive_income = st.number_input("Passive/Rental Corporate Income (€)", min_value=0.00, value=0.00)
    with c_col2:
        trading_tax_due = net_taxable_profit * 0.125
        passive_tax_due = passive_income * 0.25
        total_corporate_tax = trading_tax_due + passive_tax_due
        st.metric("Total Corporate Tax Due", f"€{total_corporate_tax:,.2f}")

# ==========================================
# 5. INVOICE INGESTION & AUTOMATED VAT PARSING
# ==========================================
st.header("🧾 Invoice Intake Hub")
invoice_file = st.file_uploader("Upload Invoices (Excel/CSV/Xero)", type=["csv", "xlsx"])

if invoice_file is not None:
    inv_df = pd.read_excel(invoice_file) if invoice_file.name.endswith('.xlsx') else pd.read_csv(invoice_file)
    inv_df.rename(columns={'*ContactName': 'Customer', 'InvoiceNumber': 'Doc_ID', 'Subtotal': 'Net', 'TaxType': 'Tax_Rule'}, inplace=True, errors='ignore')
    
    if 'Net' in inv_df.columns:
        def match_tax(row):
            net = float(str(row['Net']).replace(',', ''))
            rule = str(row.get('Tax_Rule', 'Standard')).strip()
            rate = 0.00 if "Zero" in rule or "Exempt" in rule else client_meta["default_vat"]
            vat = net * rate
            return pd.Series([rate*100, vat, net + vat])
            
        inv_df[['Rate_%', 'VAT_Value', 'Gross']] = inv_df.apply(match_tax, axis=1)
        st.dataframe(inv_df, use_container_width=True)
        st.metric("Extracted VAT Liability", f"€{inv_df['VAT_Value'].sum():,.2f}")

# ==========================================
# 6. VISUAL REPRESENTATION ENGINE
# ==========================================
st.header("📈 Financial Performance Visuals")

chart_data = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Income': [15000, 18000, 21000, 19000, 24000, 29000],
    'Expenses': [7000, 8500, 9000, 9500, 11000, 12500]
})

col_v1, col_v2 = st.columns(2)
with col_v1:
    fig_bar = px.bar(chart_data, x='Month', y=['Income', 'Expenses'], barmode='group', title='Monthly Income vs Expenditure Flow')
    st.plotly_chart(fig_bar, use_container_width=True)
with col_v2:
    fig_line = px.line(chart_data, x='Month', y='Income', title='Annualized Revenue Scaling Trend')
    st.plotly_chart(fig_line, use_container_width=True)
