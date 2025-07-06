import streamlit as st
import pandas as pd
import plotly.express as px

# Set page layout
st.set_page_config(page_title="🚖 Ola Ride Analytics", layout="wide")

st.title("🚖 Ola Ride Analysis Dashboard")

# Upload CSV
uploaded_file = st.file_uploader("📤 Upload your Ola Ride CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Normalize booking status
    df['Booking_Status'] = df['Booking_Status'].astype(str).str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # -- Sidebar Filters --
    st.sidebar.header("🔍 Filter Options")

    # Booking Status Filter
    all_statuses = df['Booking_Status'].dropna().unique().tolist()
    booking_status_filter = st.sidebar.multiselect("Booking Status", options=['Total Booking'] + all_statuses, default=['Total Booking'])

    # Filter Booking Status
    if "Total Booking" in booking_status_filter:
        df_filtered = df[df['Booking_Status'].notna()]
    else:
        df_filtered = df[df['Booking_Status'].isin(booking_status_filter)]

    # Vehicle Type Filter
    vehicle_options = df['Vehicle_Type'].dropna().unique().tolist()
    selected_vehicles = st.sidebar.multiselect("Vehicle Type", options=["All Vehicle"] + vehicle_options, default=["All Vehicle"])
    if "All Vehicle" not in selected_vehicles:
        df_filtered = df_filtered[df_filtered['Vehicle_Type'].isin(selected_vehicles)]

    # Date Filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    df_filtered = df_filtered[(df_filtered['Date'] >= pd.to_datetime(date_range[0])) & (df_filtered['Date'] <= pd.to_datetime(date_range[1]))]

    # Payment Method Filter
    payment_options = df['Payment_Method'].dropna().unique().tolist()
    selected_payments = st.sidebar.multiselect("Payment Method", options=["All Payment Methods"] + payment_options, default=["All Payment Methods"])
    if "All Payment Methods" not in selected_payments:
        df_filtered = df_filtered[df_filtered['Payment_Method'].isin(selected_payments)]

    # --- METRICS ---
    st.subheader("📊 Key Metrics")
    total_rides = len(df_filtered)
    total_revenue = df_filtered['Booking_Value'].sum()
    avg_distance = df_filtered['Ride_Distance'].mean()
    total_distance = df_filtered['Ride_Distance'].sum()
    cancel_rate = df_filtered[df_filtered['Booking_Status'].isin(['Canceled by Customer', 'Canceled by Driver', 'Driver Not Found'])].shape[0] / total_rides * 100 if total_rides else 0

    col1, col2, col3, col4, col5= st.columns(5)
    col1.metric("🚗 Total Rides", f"{total_rides:,}")
    col2.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    col3.metric("📏 Avg Distance", f"{avg_distance:.2f} km")
    col4.metric("❌ Cancel Rate", f"{cancel_rate:.2f}%")
    col5.metric("📍 Total Distance", f"{total_distance:,.0f} km")

    # --- VISUALIZATIONS ---

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

        # Pie Chart: Canceled Rides by Customer - Reasons
    st.subheader("🙋‍♂️ Customer Cancellation Reasons")

    if 'Canceled_Rides_by_Customer' in df.columns:
        customer_cancel = df['Canceled_Rides_by_Customer'].dropna()
        customer_cancel_counts = customer_cancel.value_counts().reset_index()
        customer_cancel_counts.columns = ['Reason', 'Count']

        if not customer_cancel_counts.empty:
            fig_customer_cancel = px.pie(
                customer_cancel_counts,
                names='Reason',
                values='Count',
                title='Reasons for Cancellation by Customers',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            st.plotly_chart(fig_customer_cancel, use_container_width=True)
        else:
            st.info("No customer cancellation reasons found.")
    else:
        st.warning("❗ Column 'Canceled_Rides_by_Customer' not found in the dataset.")

    # Pie Chart: Canceled Rides by Driver - Reasons
    st.subheader("🚖 Driver Cancellation Reasons")

    if 'Canceled_Rides_by_Driver' in df.columns:
        driver_cancel = df['Canceled_Rides_by_Driver'].dropna()
        driver_cancel_counts = driver_cancel.value_counts().reset_index()
        driver_cancel_counts.columns = ['Reason', 'Count']

        if not driver_cancel_counts.empty:
            fig_driver_cancel = px.pie(
                driver_cancel_counts,
                names='Reason',
                values='Count',
                title='Reasons for Cancellation by Drivers',
                color_discrete_sequence=px.colors.sequential.Oranges
            )
            st.plotly_chart(fig_driver_cancel, use_container_width=True)
        else:
            st.info("No driver cancellation reasons found.")
    else:
        st.warning("❗ Column 'Canceled_Rides_by_Driver' not found in the dataset.")


    # Optional: Ride Volume Over Time
    st.subheader("📅 Ride Volume Over Time")
    daily_rides = df_filtered.groupby('Date').size().reset_index(name='Total Rides')
    fig_volume = px.line(daily_rides, x='Date', y='Total Rides', title='Ride Volume Trend', markers=True)    # Peak Ride Hours Analysis
    st.subheader("⏰ Peak Ride Hours")

    if 'Time' in df_filtered.columns:
        # Convert Time column to datetime if it's not already
        df_filtered['Time'] = pd.to_datetime(df_filtered['Time'], errors='coerce')

        # Extract hour
        df_filtered['Hour'] = df_filtered['Time'].dt.hour

        # Group by hour
        hour_counts = df_filtered['Hour'].value_counts().reset_index()
        hour_counts.columns = ['Hour', 'Total Rides']
        hour_counts = hour_counts.sort_values('Hour')  # Sort by hour

        # Plot
        fig_hourly = px.bar(hour_counts, x='Hour', y='Total Rides',
                            title='Ride Distribution by Hour of Day',
                            labels={'Hour': 'Hour of Day', 'Total Rides': 'Ride Count'},
                            color='Total Rides',
                            color_continuous_scale='Blues')
        st.plotly_chart(fig_hourly, use_container_width=True)
    else:
        st.warning("🕒 'Time' column not found in the dataset.")

    st.plotly_chart(fig_volume, use_container_width=True)

        # Pie Chart: Booking Status Breakdown
    st.subheader("📊 Booking Status Breakdown")
    fig_status_pie = px.pie(
        status_counts,
        names='Booking_Status',
        values='Count',
        title='Booking Status Breakdown',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig_status_pie.update_traces(
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
    )
    st.plotly_chart(fig_status_pie, use_container_width=True)

    # --- Vehicle Type vs Ratings ---
    st.subheader("⭐ Vehicle Type vs Ratings")

    # Ensure ratings are numeric
    df_filtered['Driver_Rating'] = pd.to_numeric(df_filtered['Driver_Ratings'], errors='coerce')
    df_filtered['Customer_Rating'] = pd.to_numeric(df_filtered['Customer_Rating'], errors='coerce')

    # Group by vehicle type and calculate average ratings
    rating_df = df_filtered.groupby('Vehicle_Type')[['Driver_Ratings', 'Customer_Rating']].mean().reset_index()

    # Melt for better plotting
    rating_melted = rating_df.melt(id_vars='Vehicle_Type', value_vars=['Driver_Ratings', 'Customer_Rating'],
                                   var_name='Rating_Type', value_name='Average_Rating')

    # Plot as bar chart
    fig_ratings = px.bar(
        rating_melted,
        x='Vehicle_Type',
        y='Average_Rating',
        color='Rating_Type',
        barmode='group',
        title="⭐ Average Ratings by Vehicle Type",
        labels={'Average_Rating': 'Average Rating'},
        color_discrete_map={
            'Driver_Rating': 'steelblue',
            'Customer_Rating': 'orange'
        }
    )

    fig_ratings.update_layout(yaxis=dict(tickmode='linear', tick0=0, dtick=0.5), yaxis_range=[0, 5])

    st.plotly_chart(fig_ratings, use_container_width=True)

