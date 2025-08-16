import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page setup ---
st.set_page_config(page_title="🚖 Ola Ride Analytics", layout="wide")
st.title("🚖 Ola Ride Analytics")

# --- Upload CSV ---
uploaded_file = st.file_uploader("📤 Upload your Ola Ride CSV file", type="csv")

if not uploaded_file:
    st.info("Upload a CSV to enable the dashboard and case studies.")
else:
    # ================== DATA & FILTERS (shared) ==================
    df = pd.read_csv(uploaded_file)

    # Normalize fields
    df['Booking_Status'] = df['Booking_Status'].astype(str).str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")

    # Booking Status
    all_statuses = df['Booking_Status'].dropna().unique().tolist()
    booking_status_filter = st.sidebar.multiselect(
        "Booking Status", options=['Total Booking'] + all_statuses, default=['Total Booking']
    )
    if "Total Booking" in booking_status_filter:
        df_filtered = df[df['Booking_Status'].notna()]
    else:
        df_filtered = df[df['Booking_Status'].isin(booking_status_filter)]

    # Vehicle Type
    vehicle_options = df['Vehicle_Type'].dropna().unique().tolist()
    selected_vehicles = st.sidebar.multiselect(
        "Vehicle Type", options=["All Vehicle"] + vehicle_options, default=["All Vehicle"]
    )
    if "All Vehicle" not in selected_vehicles:
        df_filtered = df_filtered[df_filtered['Vehicle_Type'].isin(selected_vehicles)]

    # Date Range
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.sidebar.date_input(
        "Date Range", [min_date, max_date], min_value=min_date, max_value=max_date
    )
    df_filtered = df_filtered[
        (df_filtered['Date'] >= pd.to_datetime(date_range[0])) &
        (df_filtered['Date'] <= pd.to_datetime(date_range[1]))
    ]

    # Payment Method
    payment_options = df['Payment_Method'].dropna().unique().tolist()
    selected_payments = st.sidebar.multiselect(
        "Payment Method", options=["All Payment Methods"] + payment_options, default=["All Payment Methods"]
    )
    if "All Payment Methods" not in selected_payments:
        df_filtered = df_filtered[df_filtered['Payment_Method'].isin(selected_payments)]

    # ================== TABS (render ONLY after upload) ==================
    tab1, tab2 = st.tabs(["📊 Dashboard", "💼 Business Case Studies"])

    # ------------------- TAB 1: DASHBOARD -------------------
    with tab1:
        st.header("📊 Key Metrics")
        total_rides = len(df_filtered)
        total_revenue = df_filtered['Booking_Value'].sum()
        avg_distance = df_filtered['Ride_Distance'].mean()
        total_distance = df_filtered['Ride_Distance'].sum()
        cancel_rate = (
            df_filtered[df_filtered['Booking_Status'].isin(['Canceled by Customer', 'Canceled by Driver', 'Driver Not Found'])].shape[0]
            / total_rides * 100 if total_rides else 0
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🚗 Total Rides", f"{total_rides:,}")
        c2.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
        c3.metric("📏 Avg Distance", f"{avg_distance:.2f} km")
        c4.metric("❌ Cancel Rate", f"{cancel_rate:.2f}%")
        c5.metric("📍 Total Distance", f"{total_distance:,.0f} km")

        # Daily Revenue
        st.subheader("📈 Daily Revenue")
        daily_revenue = df_filtered.groupby('Date')['Booking_Value'].sum().reset_index()
        fig_revenue = px.line(daily_revenue, x='Date', y='Booking_Value', title='Daily Revenue', markers=True)
        st.plotly_chart(fig_revenue, use_container_width=True)

        # Rides by Booking Status
        st.subheader("📋 Rides by Booking Status")
        status_counts = df_filtered['Booking_Status'].value_counts().reset_index()
        status_counts.columns = ['Booking_Status', 'Count']
        fig_status = px.bar(status_counts, x='Booking_Status', y='Count', color='Booking_Status', title='Booking Status Distribution')
        st.plotly_chart(fig_status, use_container_width=True)

        # Revenue by Payment Method
        st.subheader("💳 Revenue by Payment Method")
        payment_revenue = df_filtered.groupby('Payment_Method')['Booking_Value'].sum().reset_index()
        fig_payment = px.pie(payment_revenue, values='Booking_Value', names='Payment_Method', title='Revenue by Payment Method')
        st.plotly_chart(fig_payment, use_container_width=True)

        # Customer Cancellation Reasons
        st.subheader("🙋‍♂️ Customer Cancellation Reasons")
        if 'Canceled_Rides_by_Customer' in df.columns:
            customer_cancel = df['Canceled_Rides_by_Customer'].dropna()
            customer_cancel_counts = customer_cancel.value_counts().reset_index()
            customer_cancel_counts.columns = ['Reason', 'Count']
            if not customer_cancel_counts.empty:
                fig_customer_cancel = px.pie(customer_cancel_counts, names='Reason', values='Count',
                                             title='Reasons for Cancellation by Customers',
                                             color_discrete_sequence=px.colors.sequential.Blues)
                st.plotly_chart(fig_customer_cancel, use_container_width=True)
            else:
                st.info("No customer cancellation reasons found.")
        else:
            st.warning("❗ Column 'Canceled_Rides_by_Customer' not found in the dataset.")

        # Driver Cancellation Reasons
        st.subheader("🚖 Driver Cancellation Reasons")
        if 'Canceled_Rides_by_Driver' in df.columns:
            driver_cancel = df['Canceled_Rides_by_Driver'].dropna()
            driver_cancel_counts = driver_cancel.value_counts().reset_index()
            driver_cancel_counts.columns = ['Reason', 'Count']
            if not driver_cancel_counts.empty:
                fig_driver_cancel = px.pie(driver_cancel_counts, names='Reason', values='Count',
                                           title='Reasons for Cancellation by Drivers',
                                           color_discrete_sequence=px.colors.sequential.Oranges)
                st.plotly_chart(fig_driver_cancel, use_container_width=True)
            else:
                st.info("No driver cancellation reasons found.")
        else:
            st.warning("❗ Column 'Canceled_Rides_by_Driver' not found in the dataset.")

        # Ride Volume Over Time
        st.subheader("📅 Ride Volume Over Time")
        daily_rides = df_filtered.groupby('Date').size().reset_index(name='Total Rides')
        fig_volume = px.line(daily_rides, x='Date', y='Total Rides', title='Ride Volume Trend', markers=True)
        st.plotly_chart(fig_volume, use_container_width=True)

        # Peak Ride Hours
        st.subheader("⏰ Peak Ride Hours")
        if 'Time' in df_filtered.columns:
            df_filtered['Time'] = pd.to_datetime(df_filtered['Time'], errors='coerce')
            df_filtered['Hour'] = df_filtered['Time'].dt.hour
            hour_counts = df_filtered['Hour'].value_counts().reset_index()
            hour_counts.columns = ['Hour', 'Total Rides']
            hour_counts = hour_counts.sort_values('Hour')
            fig_hourly = px.bar(hour_counts, x='Hour', y='Total Rides',
                                title='Ride Distribution by Hour of Day',
                                labels={'Hour': 'Hour of Day', 'Total Rides': 'Ride Count'},
                                color='Total Rides', color_continuous_scale='Blues')
            st.plotly_chart(fig_hourly, use_container_width=True)
        else:
            st.warning("🕒 'Time' column not found in the dataset.")

        # Booking Status Breakdown (Pie)
        st.subheader("📊 Booking Status Breakdown")
        fig_status_pie = px.pie(status_counts, names='Booking_Status', values='Count',
                                title='Booking Status Breakdown',
                                color_discrete_sequence=px.colors.sequential.Plasma)
        fig_status_pie.update_traces(
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )
        st.plotly_chart(fig_status_pie, use_container_width=True)

        # Vehicle Type vs Ratings (kept as in your code)
        st.subheader("⭐ Vehicle Type vs Ratings")
        df_filtered['Driver_Rating'] = pd.to_numeric(df_filtered['Driver_Ratings'], errors='coerce')
        df_filtered['Customer_Rating'] = pd.to_numeric(df_filtered['Customer_Rating'], errors='coerce')
        rating_df = df_filtered.groupby('Vehicle_Type')[['Driver_Ratings', 'Customer_Rating']].mean().reset_index()
        rating_melted = rating_df.melt(id_vars='Vehicle_Type',
                                       value_vars=['Driver_Ratings', 'Customer_Rating'],
                                       var_name='Rating_Type', value_name='Average_Rating')
        fig_ratings = px.bar(rating_melted, x='Vehicle_Type', y='Average_Rating',
                             color='Rating_Type', barmode='group',
                             title="⭐ Average Ratings by Vehicle Type",
                             labels={'Average_Rating': 'Average Rating'},
                             color_discrete_map={'Driver_Rating': 'steelblue', 'Customer_Rating': 'orange'})
        fig_ratings.update_layout(yaxis=dict(tickmode='linear', tick0=0, dtick=0.5), yaxis_range=[0, 5])
        st.plotly_chart(fig_ratings, use_container_width=True)

    # ------------------- TAB 2: BUSINESS CASE STUDIES -------------------
    with tab2:
        st.header("💼 Business Case Studies")

        case_option = st.selectbox(
            "📌 Select a Business Case Study:",
            [
                "1. Identifying Peak Demand Hours & Optimizing Driver Allocation",
                "2. Analyzing Customer Behavior for Personalized Marketing",
                "3. Understanding Pricing Patterns & Surge Pricing Effectiveness",
                "4. Detecting Anomalies or Fraudulent Activities in Ride Data"
            ]
        )

        # Case Study 1
        if case_option.startswith("1"):
            
            if "Time" in df_filtered.columns:
                df_filtered['Hour'] = pd.to_datetime(df_filtered['Time'], errors='coerce').dt.hour
                hourly = df_filtered.groupby('Hour').size().reset_index(name='Total Rides')
                cancel_hourly = df_filtered[df_filtered['Booking_Status'].isin(
                    ['Canceled by Customer', 'Canceled by Driver', 'Driver Not Found']
                )].groupby('Hour').size().reset_index(name='Cancelled Rides')
                merged = pd.merge(hourly, cancel_hourly, on='Hour', how='left').fillna(0)
                merged['Cancel Rate %'] = (merged['Cancelled Rides'] / merged['Total Rides']) * 100

                fig_hour = px.bar(merged, x='Hour', y='Total Rides',
                                  title="🚗 Rides by Hour of Day", color='Total Rides')
                fig_cancel = px.line(merged, x='Hour', y='Cancel Rate %',
                                     title="❌ Cancellation Rate by Hour", markers=True)
                st.plotly_chart(fig_hour, use_container_width=True)
                st.plotly_chart(fig_cancel, use_container_width=True)
            else:
                st.warning("🕒 'Time' column not found in the dataset.")

            st.markdown("- Allocate more drivers to busiest hours.\n- Investigate high-cancel hours for supply gaps.")

        # Case Study 2
        elif case_option.startswith("2"):
            top_customers = df_filtered['Customer_ID'].value_counts().reset_index()
            top_customers.columns = ['Customer_ID', 'Total Rides']
            fig_cust = px.bar(top_customers.head(10), x='Customer_ID', y='Total Rides',
                              title="👥 Top 10 Customers by Ride Count")
            st.plotly_chart(fig_cust, use_container_width=True)

            spend = df_filtered.groupby('Customer_ID')['Booking_Value'].mean().reset_index()
            spend = spend.sort_values('Booking_Value', ascending=False)
            fig_spend = px.bar(spend.head(10), x='Customer_ID', y='Booking_Value',
                               title="💰 Top 10 Customers by Avg Spend")
            st.plotly_chart(fig_spend, use_container_width=True)

            pay_pref = df_filtered['Payment_Method'].value_counts().reset_index()
            pay_pref.columns = ['Payment_Method', 'Count']
            fig_pay = px.pie(pay_pref, names='Payment_Method', values='Count',
                             title="💳 Preferred Payment Methods")
            st.plotly_chart(fig_pay, use_container_width=True)

            st.markdown("- Reward loyal, high-spend users.\n- Payment-based targeting for campaigns.")

        # Case Study 3
        elif case_option.startswith("3"):
            df_filtered['Fare_per_km'] = df_filtered['Booking_Value'] / df_filtered['Ride_Distance']
            price_summary = df_filtered.groupby('Vehicle_Type')['Fare_per_km'].mean().reset_index()
            fig_price = px.bar(price_summary, x='Vehicle_Type', y='Fare_per_km',
                               title="💵 Avg Fare per Km by Vehicle Type")
            st.plotly_chart(fig_price, use_container_width=True)

            if "Time" in df_filtered.columns:
                # ensure Hour exists even if Case 1 wasn't selected
                df_filtered['Hour'] = pd.to_datetime(df_filtered['Time'], errors='coerce').dt.hour
                surge = df_filtered.groupby('Hour')['Fare_per_km'].mean().reset_index()
                fig_surge = px.line(surge, x='Hour', y='Fare_per_km',
                                    title="📈 Avg Fare per Km by Hour (Possible Surge)", markers=True)
                st.plotly_chart(fig_surge, use_container_width=True)
            else:
                st.warning("🕒 'Time' column not found; surge-by-hour view unavailable.")

            st.markdown("- Spot peak-hour surge effects.\n- Compare profitability by vehicle class.")

        # Case Study 4
        elif case_option.startswith("4"):
            df_filtered['Fare_per_km'] = df_filtered['Booking_Value'] / df_filtered['Ride_Distance']

            fig_anomaly = px.box(df_filtered, y='Fare_per_km', points="all",
                                 title="📦 Fare per Km Distribution (Outliers = Possible Fraud)")
            st.plotly_chart(fig_anomaly, use_container_width=True)

            suspicious = df_filtered[(df_filtered['Ride_Distance'] < 0.5) & (df_filtered['Booking_Value'] > 200)]
            if not suspicious.empty:
                st.warning("⚠️ Suspicious rides detected (very low distance but high value):")
                st.dataframe(suspicious[['Booking_ID', 'Customer_ID', 'Ride_Distance', 'Booking_Value']])
            else:
                st.success("✅ No suspicious rides found in current filters.")

            st.markdown("- Outlier fares/km\n- Short distance, high fare checks\n- Repeated cancellations by same user")
