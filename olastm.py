import streamlit as st # Streamlit is used to build interactive web apps for data science and machine learning.
import pandas as pd # It is used for data manipulation and data analysis.
import plotly.express as px # It's used for creating interactive plots and charts.

# Set page layout
st.set_page_config(page_title="🚖 Ola Ride Analytics", layout="wide")
# st.set_page_config: Configures the layout and title of the web page.
# page_title: Sets the browser tab's title.
# layout="wide": useful for dashboards where you need more horizontal space.

st.title("🚖 Ola Ride Analysis Dashboard") # Displays a main title at the top of the Streamlit app

# Upload CSV
uploaded_file = st.file_uploader("📤 Upload your Ola Ride CSV file", type="csv") # Creates a file uploader widget in the app, allowing the user to upload a .csv file.

if uploaded_file:
    df = pd.read_csv(uploaded_file) # reads it into a Pandas DataFrame called df

    # Normalize booking status
    df['Booking_Status'] = df['Booking_Status'].astype(str).str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # .astype: Converts every value in that column to a string, just in case some values were stored as numbers, NaN, or any other type.
    # .str.strip: Applies the .strip() function to remove leading and trailing spaces from each string value.

    # -- Sidebar Filters --
    st.sidebar.header("🔍 Filter Options")

    # Booking Status Filter
    all_statuses = df['Booking_Status'].dropna().unique().tolist()
    booking_status_filter = st.sidebar.multiselect("Booking Status", options=['Total Booking'] + all_statuses, default=['Total Booking'])

    # .dropna(): Removes any rows where the value in "Booking_Status" is NaN (missing).
    # .unique(): Returns the unique values in the column after dropping NaN.
    # .tolist(): Converts the NumPy array of unique values into a Python list.

    # Filter Booking Status
    if "Total Booking" in booking_status_filter:
        df_filtered = df[df['Booking_Status'].notna()] # .notna(): checks the missing values
    else:
        df_filtered = df[df['Booking_Status'].isin(booking_status_filter)] # .isin: checks if each row’s status is in that list.

    # Vehicle Type Filter
    vehicle_options = df['Vehicle_Type'].dropna().unique().tolist()
    selected_vehicles = st.sidebar.multiselect("Vehicle Type", options=["All Vehicle"] + vehicle_options, default=["All Vehicle"])
    if "All Vehicle" not in selected_vehicles:
        df_filtered = df_filtered[df_filtered['Vehicle_Type'].isin(selected_vehicles)] # Keeps only rows where Vehicle_Type matches the selected ones.

    # Date Filter
    min_date = df['Date'].min() # Used to set the default start date and the minimum selectable date
    max_date = df['Date'].max() # Used to set the default end date and the maximum selectable date
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    df_filtered = df_filtered[(df_filtered['Date'] >= pd.to_datetime(date_range[0])) & (df_filtered['Date'] <= pd.to_datetime(date_range[1]))]

    # [min_date, max_date]: The default value — the entire date span.
    # min_value=min_date: User can’t pick dates earlier than this.
    # max_value=max_date: User can’t pick dates later than this.
    # date_range[0]: The start date selected by the user.
    # date_range[1]: The end date selected by the user.
    # pd.to_datetime: Ensures the selected dates are converted to proper datetime format

    # Payment Method Filter
    payment_options = df['Payment_Method'].dropna().unique().tolist()
    selected_payments = st.sidebar.multiselect("Payment Method", options=["All Payment Methods"] + payment_options, default=["All Payment Methods"])
    if "All Payment Methods" not in selected_payments:
        df_filtered = df_filtered[df_filtered['Payment_Method'].isin(selected_payments)]

    # --- METRICS ---
    st.subheader("📊 Key Metrics")
    total_rides = len(df_filtered) # total number of rides after all filters are applied
    total_revenue = df_filtered['Booking_Value'].sum()
    avg_distance = df_filtered['Ride_Distance'].mean() # .mean() to find the average of the Ride_Distance column.
    total_distance = df_filtered['Ride_Distance'].sum()
    cancel_rate = df_filtered[df_filtered['Booking_Status'].isin(['Canceled by Customer', 'Canceled by Driver', 'Driver Not Found'])].shape[0] / total_rides * 100 if total_rides else 0

    # df_filtered['Booking_Status'].isin(): Creates a Boolean mask for rides that were cancelled — either by customer, driver, or due to driver not found.
    # df_filtered[]: Filters only the cancelled rides.
    # .shape[0]: Gets the number of cancelled rides.
    # / total_rides * 100: Divides by total rides to get the cancellation rate as a percentage.
    # if total_rides else 0: Handles the edge case where total_rides is 0 (to avoid division by zero).
    # If there are no rides, cancellation rate is shown as 0%.

    col1, col2, col3, col4, col5= st.columns(5)
    col1.metric("🚗 Total Rides", f"{total_rides:,}") # f"{total_rides:,}": Formats the number with comma separators (e.g., 1,234 instead of 1234).
    col2.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    col3.metric("📏 Avg Distance", f"{avg_distance:.2f} km")
    col4.metric("❌ Cancel Rate", f"{cancel_rate:.2f}%")
    col5.metric("📍 Total Distance", f"{total_distance:,.0f} km")

    # --- VISUALIZATIONS ---

    # Daily Revenue
    st.subheader("📈 Daily Revenue")
    daily_revenue = df_filtered.groupby('Date')['Booking_Value'].sum().reset_index() # .reset_index(): Converts the grouped result back into a regular DataFrame with a new index.
    fig_revenue = px.line(daily_revenue, x='Date', y='Booking_Value', title='Daily Revenue', markers=True) # markers=True: Adds dot markers on each data point, making the trend easier to follow.
    st.plotly_chart(fig_revenue, use_container_width=True) # use_container_width=True: Makes the chart automatically resize to fit the full width of its container

    # Rides by Booking Status
    st.subheader("📋 Rides by Booking Status") # introduces the chart that shows ride distribution by status.
    status_counts = df_filtered['Booking_Status'].value_counts().reset_index() # .value_counts(): Counts how many times each unique status appears.
    status_counts.columns = ['Booking_Status', 'Count']
    fig_status = px.bar(status_counts, x='Booking_Status', y='Count', color='Booking_Status', title='Booking Status Distribution') # color='Booking_Status': Colors each bar differently based on status.
    st.plotly_chart(fig_status, use_container_width=True)

    # Revenue by Payment Method
    st.subheader("💳 Revenue by Payment Method") 
    payment_revenue = df_filtered.groupby('Payment_Method')['Booking_Value'].sum().reset_index()
    fig_payment = px.pie(payment_revenue, values='Booking_Value', names='Payment_Method', title='Revenue by Payment Method')
    st.plotly_chart(fig_payment, use_container_width=True)

        # Pie Chart: Canceled Rides by Customer - Reasons
    st.subheader("🙋‍♂️ Customer Cancellation Reasons")

    if 'Canceled_Rides_by_Customer' in df.columns: # Ensures that the dataset (df) actually contains a column called 'Canceled_Rides_by_Customer'
        customer_cancel = df['Canceled_Rides_by_Customer'].dropna() # Selects the column and drops any null values and includes rows where a cancellation reason is present.
        customer_cancel_counts = customer_cancel.value_counts().reset_index() # .value_counts(): Counts how many times each reason appears.
        customer_cancel_counts.columns = ['Reason', 'Count']

        if not customer_cancel_counts.empty: # Checks if there are any non-empty results prevents rendering no data.
            fig_customer_cancel = px.pie(
                customer_cancel_counts,
                names='Reason',
                values='Count',
                title='Reasons for Cancellation by Customers',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            st.plotly_chart(fig_customer_cancel, use_container_width=True)
        else:
            st.info("No customer cancellation reasons found.") # If customer_cancel_counts is empty (i.e., no reasons found after filtering), shows a friendly info message.
    else:
        st.warning("❗ Column 'Canceled_Rides_by_Customer' not found in the dataset.") # If the column is not present at all, shows a warning message

    # Pie Chart: Canceled Rides by Driver - Reasons
    st.subheader("🚖 Driver Cancellation Reasons")

    if 'Canceled_Rides_by_Driver' in df.columns:  # Checks if the dataset (df) contains the column 'Canceled_Rides_by_Driver'.
        driver_cancel = df['Canceled_Rides_by_Driver'].dropna() # Renoves any null value and Keeps only the rows where a cancellation reason was provided.
        driver_cancel_counts = driver_cancel.value_counts().reset_index() # Counts the occurrences of each unique cancellation reason by the driver.  # .reset_index() turns it into a DataFrame.
        driver_cancel_counts.columns = ['Reason', 'Count']

        if not driver_cancel_counts.empty: # prevents rendering any empty chart
            fig_driver_cancel = px.pie(
                driver_cancel_counts,
                names='Reason',
                values='Count',
                title='Reasons for Cancellation by Drivers',
                color_discrete_sequence=px.colors.sequential.Oranges
            )
            st.plotly_chart(fig_driver_cancel, use_container_width=True)
        else:
            st.info("No driver cancellation reasons found.") # Displays an info message if the column exists but has no non-null values.
    else:
        st.warning("❗ Column 'Canceled_Rides_by_Driver' not found in the dataset.") # Displays a warning message if the column is not present


    # Optional: Ride Volume Over Time
    st.subheader("📅 Ride Volume Over Time")
    daily_rides = df_filtered.groupby('Date').size().reset_index(name='Total Rides')
    fig_volume = px.line(daily_rides, x='Date', y='Total Rides', title='Ride Volume Trend', markers=True)    
    
    # Peak Ride Hours Analysis
    st.subheader("⏰ Peak Ride Hours")

    if 'Time' in df_filtered.columns:
        # Converts it to datetime and extracts the hour (0 to 23).
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
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>" # hover template to show count and percentage.
    )
    st.plotly_chart(fig_status_pie, use_container_width=True)

    # --- Vehicle Type vs Ratings ---
    st.subheader("⭐ Vehicle Type vs Ratings")

    # Ensure ratings are numeric
    df_filtered['Driver_Rating'] = pd.to_numeric(df_filtered['Driver_Ratings'], errors='coerce')
    df_filtered['Customer_Rating'] = pd.to_numeric(df_filtered['Customer_Rating'], errors='coerce')
    # errors='coerce': If any value is not a number (e.g., text), it's replaced with NaN.
    
    # Group by vehicle type and calculate average ratings
    rating_df = df_filtered.groupby('Vehicle_Type')[['Driver_Ratings', 'Customer_Rating']].mean().reset_index() # .reset_index(): converts back to dataframe

    # Melt for better plotting
    # This reshapes the DataFrame from wide to long format, suited for grouped bar plots.
    rating_melted = rating_df.melt(id_vars='Vehicle_Type', value_vars=['Driver_Ratings', 'Customer_Rating'],
                                   var_name='Rating_Type', value_name='Average_Rating')

    # Plot as bar chart
    fig_ratings = px.bar(
        rating_melted,
        x='Vehicle_Type',
        y='Average_Rating',
        color='Rating_Type', # Separates bars by rating type (Driver vs Customer).
        barmode='group', # Places bars side-by-side 
        title="⭐ Average Ratings by Vehicle Type",
        labels={'Average_Rating': 'Average Rating'}, # Renames y-axis label to "Average Rating" 
        color_discrete_map={
            'Driver_Rating': 'steelblue',
            'Customer_Rating': 'orange'
        }
    )

    fig_ratings.update_layout(yaxis=dict(tickmode='linear', tick0=0, dtick=0.5), yaxis_range=[0, 5]) # Y-axis starts at 0 and increases in steps of 0.5 ; Sets the rating scale between 0 and 5

    st.plotly_chart(fig_ratings, use_container_width=True)

