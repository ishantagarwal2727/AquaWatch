
import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="AquaWatch",
    page_icon="💧",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------

st.title("💧 AquaWatch")
st.subheader("Smart Water Quality Monitoring Dashboard")

st.info(
    "Educational prototype using sample readings. "
    "It does not certify water as safe for drinking."
)

# -----------------------------
# SAMPLE DATA
# -----------------------------

def sample_data():
    return pd.DataFrame({
        "Date": pd.to_datetime([
            "2026-11-01",
            "2026-11-02",
            "2026-11-03",
            "2026-11-04",
            "2026-11-05"
        ]),
        "Location": [
            "Greater Noida",
            "Knowledge Park",
            "Alpha 1",
            "Beta 2",
            "Greater Noida"
        ],
        "pH": [7.0, 7.2, 6.2, 7.5, 8.0],
        "Turbidity": [2.1, 3.0, 6.0, 2.5, 4.0],
        "TDS": [250, 300, 450, 280, 350]
    })


if "readings" not in st.session_state:
    st.session_state.readings = sample_data()


# -----------------------------
# CLEAN DATA
# -----------------------------

def clean_data(df):
    df = df.copy()

    required = [
        "Date", "Location", "pH",
        "Turbidity", "TDS"
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce"
    )

    for col in ["pH", "Turbidity", "TDS"]:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    df = df.dropna(subset=required)

    return df


# -----------------------------
# ALERT SYSTEM
# -----------------------------

def find_alerts(df):
    alerts = []

    for _, row in df.iterrows():

        date = pd.to_datetime(
            row["Date"]
        ).date()

        location = row["Location"]

        if not 6.5 <= row["pH"] <= 8.5:
            alerts.append(
                f"{date} - {location}: "
                f"pH {row['pH']} is outside "
                "the illustrative range."
            )

        if row["Turbidity"] > 5:
            alerts.append(
                f"{date} - {location}: "
                f"Turbidity {row['Turbidity']} "
                "is above the demo threshold of 5."
            )

        if row["TDS"] > 500:
            alerts.append(
                f"{date} - {location}: "
                f"TDS {row['TDS']} "
                "is above the demo threshold of 500."
            )

    return alerts


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("💧 AquaWatch Menu")

page = st.sidebar.radio(
    "Select a page",
    [
        "Dashboard",
        "Add Reading",
        "Upload CSV",
        "About Project"
    ]
)


# -----------------------------
# DASHBOARD
# -----------------------------

if page == "Dashboard":

    st.header("Water Quality Overview")

    df = clean_data(st.session_state.readings)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average pH",
        round(df["pH"].mean(), 2) if not df.empty else "N/A"
    )

    col2.metric(
        "Average Turbidity",
        round(df["Turbidity"].mean(), 2) if not df.empty else "N/A"
    )

    col3.metric(
        "Average TDS",
        round(df["TDS"].mean(), 2) if not df.empty else "N/A"
    )

    st.divider()

    st.subheader("Recorded Water Quality Data")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader("📊 Water Quality Graphs")

    if not df.empty:

        chart_data = df.set_index("Date")

        st.write("pH Level")
        st.line_chart(chart_data["pH"])

        st.write("Turbidity")
        st.line_chart(chart_data["Turbidity"])

        st.write("Total Dissolved Solids (TDS)")
        st.line_chart(chart_data["TDS"])

    st.divider()

    st.subheader("🚨 Water Quality Alerts")

    alerts = find_alerts(df)

    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("No configured alerts found.")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Water Quality Report",
        data=csv,
        file_name="aquawatch_report.csv",
        mime="text/csv"
    )


# -----------------------------
# ADD NEW READING
# -----------------------------

elif page == "Add Reading":

    st.header("➕ Add New Water Reading")

    with st.form("reading_form"):

        date = st.date_input("Select Date")

        location = st.text_input(
            "Enter Location",
            placeholder="Greater Noida"
        )

        ph = st.number_input(
            "pH Level",
            min_value=0.0,
            max_value=14.0,
            value=7.0
        )

        turbidity = st.number_input(
            "Turbidity (NTU)",
            min_value=0.0,
            value=2.0
        )

        tds = st.number_input(
            "TDS (mg/L)",
            min_value=0.0,
            value=250.0
        )

        submit = st.form_submit_button(
            "Save Reading"
        )

        if submit:

            if not location.strip():
                st.error("Please enter a location.")

            else:

                new_reading = pd.DataFrame([{
                    "Date": pd.to_datetime(date),
                    "Location": location,
                    "pH": ph,
                    "Turbidity": turbidity,
                    "TDS": tds
                }])

                st.session_state.readings = pd.concat(
                    [
                        st.session_state.readings,
                        new_reading
                    ],
                    ignore_index=True
                )

                st.success(
                    "Water quality reading added successfully!"
                )


# -----------------------------
# CSV UPLOAD
# -----------------------------

elif page == "Upload CSV":

    st.header("📁 Upload Water Quality CSV")

    st.write(
        "Your CSV must contain these columns:"
    )

    st.code(
        "Date,Location,pH,Turbidity,TDS"
    )

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            uploaded_data = pd.read_csv(uploaded_file)

            uploaded_data = clean_data(uploaded_data)

            if uploaded_data.empty:
                st.error("No valid readings found.")

            else:

                st.session_state.readings = uploaded_data

                st.success("CSV uploaded successfully!")

                st.dataframe(
                    uploaded_data,
                    use_container_width=True
                )

        except Exception as error:

            st.error(
                f"CSV upload error: {error}"
            )


# -----------------------------
# ABOUT PROJECT
# -----------------------------

elif page == "About Project":

    st.header("About AquaWatch")

    st.write("""
    AquaWatch is a Smart Water Quality Monitoring
    and Awareness Dashboard.

    Project Objectives:

    1. Make water quality information easier to understand.
    2. Monitor pH, Turbidity and TDS readings.
    3. Display water quality graphs.
    4. Identify readings that cross configured thresholds.
    5. Support environmental awareness.

    Technology Used:

    - Python
    - Streamlit
    - Pandas

    Sustainable Development Goal:

    SDG 6 - Clean Water and Sanitation.

    This is an educational software prototype.
    It does not replace laboratory water testing.
    """)

    st.success("Thank you for visiting AquaWatch!")
