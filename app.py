import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pandas import ExcelWriter
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

st.set_page_config(page_title="Agentic Report Generator", layout="wide")
st.title("🤖 Agentic AI – Manufacturing Report Generator")

uploaded_file = st.file_uploader("📤 Upload your manufacturing CSV file", type=["csv"])

# === Report Functions ===
def generate_units_by_product(df):
    return df.groupby("Product Type")["Units Produced"].sum().reset_index()

def generate_avg_defects_by_shift(df):
    return df.groupby("Shift")["Defects"].mean().reset_index()

def generate_monthly_production(df):
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df.groupby("Month")["Units Produced"].sum().reset_index()

def generate_avg_cost_summary(df):
    cols = []
    if "Material Cost Per Unit" in df.columns:
        cols.append("Material Cost Per Unit")
    if "Labour Cost Per Hour" in df.columns:
        cols.append("Labour Cost Per Hour")
    return df[cols].mean().reset_index().rename(columns={0: "Average Cost"})

def generate_energy_vs_production(df):
    return df[["Energy Consumption kWh", "Units Produced"]].corr().reset_index()

def generate_defect_rate_by_product(df):
    prod = df.groupby("Product Type")["Units Produced"].sum()
    defects = df.groupby("Product Type")["Defects"].sum()
    result = (defects / prod * 100).reset_index()
    result.columns = ["Product Type", "Defect Rate (%)"]
    return result

def generate_productivity_per_operator(df):
    df = df.copy()
    df["Productivity"] = df["Units Produced"] / (df["Operator Count"] * df["Production Time Hours"])
    return df[["Product Type", "Shift", "Productivity"]].groupby(["Product Type", "Shift"]).mean().reset_index()

def send_report_via_email(sender_email, sender_password, recipient_email, report_path):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Manufacturing Report"

    body = "Hello,\n\nHere is your requested manufacturing report attached.\n\nRegards,\nYour AI System"
    msg.attach(MIMEText(body, 'plain'))

    # Attach file
    with open(report_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename={os.path.basename(application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)}'
    )
    msg.attach(part)

    # SMTP server details (example for Gmail)
    smtp_server = "abth110405@gmail.com"
    smtp_port = 587
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

# === Main Execution ===
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    st.success("✅ File loaded successfully!")
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    st.divider()
    st.header("📊 Agent Reports & Visualizations")


    # 1. Units by Product Type
    st.subheader("Units by Product Type")
    units = generate_units_by_product(df)
    st.dataframe(units, use_container_width=True)
    fig1, ax1 = plt.subplots()
    units.plot(kind='bar', x='Product Type', y='Units Produced', ax=ax1)
    st.pyplot(fig1)

    # 2. Avg Defects by Shift
    st.subheader("Average Defects by Shift")
    defects = generate_avg_defects_by_shift(df)
    st.dataframe(defects, use_container_width=True)
    fig2, ax2 = plt.subplots()
    defects.plot(kind='bar', x='Shift', y='Defects', ax=ax2, color='salmon')
    st.pyplot(fig2)

    # 3. Monthly Production
    st.subheader("Monthly Production Trends")
    monthly = generate_monthly_production(df)
    st.dataframe(monthly, use_container_width=True)
    fig3, ax3 = plt.subplots()
    monthly.plot(kind='line', x='Month', y='Units Produced', ax=ax3, marker='o', color='green')
    st.pyplot(fig3)

    # 4. Average Cost
    st.subheader("Average Cost Summary")
    cost = generate_avg_cost_summary(df)
    st.dataframe(cost, use_container_width=True)
    fig4, ax4 = plt.subplots()
    cost.plot(kind='bar', x='index', y='Average Cost', ax=ax4, color='orange')
    st.pyplot(fig4)

    # 5. Energy vs Production
    st.subheader("Energy vs Production Correlation")
    energy = generate_energy_vs_production(df)
    st.dataframe(energy, use_container_width=True)

    # 6. Defect Rate (%)
    st.subheader("Defect Rate by Product Type")
    defect_rate = generate_defect_rate_by_product(df)
    st.dataframe(defect_rate, use_container_width=True)
    fig6, ax6 = plt.subplots()
    defect_rate.plot(kind='bar', x='Product Type', y='Defect Rate (%)', ax=ax6, color='crimson')
    st.pyplot(fig6)

    # 7. Productivity per Operator
    st.subheader("Productivity per Operator per Hour")
    productivity = generate_productivity_per_operator(df)
    st.dataframe(productivity, use_container_width=True)
    fig7, ax7 = plt.subplots()
    for shift in productivity["Shift"].unique():
        shift_df = productivity[productivity["Shift"] == shift]
        ax7.bar(shift_df["Product Type"], shift_df["Productivity"], label=f"{shift} Shift")
    ax7.set_title("Productivity per Operator")
    ax7.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig7)

    # === Export Excel Report ===
    st.divider()
    st.subheader("📁 Download Report")
    buffer = io.BytesIO()
    with ExcelWriter(buffer, engine='openpyxl') as writer:
        units.to_excel(writer, sheet_name="Units by Product", index=False)
        defects.to_excel(writer, sheet_name="Defects by Shift", index=False)
        monthly.to_excel(writer, sheet_name="Monthly Production", index=False)
        cost.to_excel(writer, sheet_name="Cost Summary", index=False)
        energy.to_excel(writer, sheet_name="Energy vs Prod", index=False)
        defect_rate.to_excel(writer, sheet_name="Defect Rate (%)", index=False)
        productivity.to_excel(writer, sheet_name="Productivity", index=False)

    st.download_button(
        label="⬇️ Download Excel Report",
        data=buffer.getvalue(),
        file_name="agentic_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


recipient = request.form.get("email")  # or wherever you get the target email
sender_email = os.getenv("221260132002setiict@gmail.com")
sender_password = os.getenv("952004")
if recipient:
    try:
        send_report_via_email(sender_email, sender_password, recipient, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
    except Exception as e:
        # log error, but don’t break user download
        app.logger.error(f"Email send failed: {e}")
