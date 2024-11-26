import pandas as pd
import mysql.connector
import streamlit as slt
from streamlit_option_menu import option_menu

# Loading route details for all states
def load_state_routes():
    state_files = {
        "Andhra Pradesh": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Andhra_Details_df.csv",
        "Kerala": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Kerala_Details_df.csv",
        "Telangana": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Telangana_Details_df.csv",
        "Kadamba": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Kadamba_Details_df.csv",
        "South Bengal": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/South_Bengal_Details_df.csv",
        "Rajasthan": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Rajasthan_Details_df.csv",
        "Himachal": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Himachal_Details_df.csv",
        "Assam": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Assam_Details_df.csv",
        "Uttar Pradesh": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/Uttar_Pradesh_Details_df.csv",
        "West Bengal": r"C:/Users/PRIYA/OneDrive/Desktop/Red_Bus_Project/West_Bengal_Details_df.csv"
    }
    
    routes = {}
    for state, file in state_files.items():
        df = pd.read_csv(file)
        routes[state] = df["Route_Names"].tolist()
    return routes

# Function to get bus details based on filters
def get_bus_details(state, route, seat_type, ac_type, rating_range, fare_range, start_time):
    conn = mysql.connector.connect(host="localhost", user="root", password="123456789", database="red_bus_details")
    my_cursor = conn.cursor()

    # Seat Type Condition (e.g., Sleeper, Sitter)
    seat_condition = {
        "Sleeper": "Bus_type LIKE '%Sleeper%'",
        "Sitter": "Bus_type NOT LIKE '%Sleeper%'"
    }[seat_type]
    
    # AC Type Condition (AC or Non-AC)
    ac_condition = {
        "AC": "Bus_type LIKE '%A/c%'",
        "Non-AC": "Bus_type NOT LIKE '%A/c%'"
    }[ac_type]

    # Rating Range Condition
    min_rating, max_rating = {
        "1 to 2": (1, 2),
        "2 to 3": (2, 3),
        "3 to 4": (3, 4),
        "4 to 5": (4, 5)
    }[rating_range]
    rating_condition = f"Ratings BETWEEN {min_rating} AND {max_rating}"

    # Fare Range Condition
    fare_min, fare_max = {
        "50-1000": (50, 1000),
        "1000-2000": (1000, 2000),
        "2000 and above": (2000, 100000)
    }[fare_range]
    fare_condition = f"Price BETWEEN {fare_min} AND {fare_max}"

    # Start Time Condition
    time_condition = f"Start_time >= '{start_time}'" if start_time else "1=1"
    
    # Query with all the filters applied
    query = f'''
        SELECT * FROM bus_details 
        WHERE Route_name = %s
        AND {seat_condition}
        AND {ac_condition}
        AND {rating_condition}
        AND {fare_condition}
        AND {time_condition}
        ORDER BY Price, Start_time
    '''
    
    my_cursor.execute(query, (route,))
    result = my_cursor.fetchall()
    conn.close()

    df = pd.DataFrame(result, columns=[
        "ID", "Bus_name", "Bus_type", "Start_time", "End_time", "Total_duration",
        "Price", "Seats_Available", "Ratings", "Route_link", "Route_name"
    ])
    return df

# Setting up Streamlit page
slt.set_page_config(layout="wide")

web = option_menu(menu_title="🚌OnlineBus",
                  options=["📍States and Routes"],
                  icons=["info-circle"],
                  orientation="horizontal")

# States and Routes page
if web == "📍States and Routes":
    routes = load_state_routes()
    state = slt.selectbox("Select State", list(routes.keys()))

    # Route dropdown
    route = slt.selectbox("Select Route", routes[state])

    # Seat Type, AC Type dropdowns
    col1, col2, col3 = slt.columns(3)
    with col1:
        seat_type = slt.selectbox("Select Seat Type", ["Sleeper", "Sitter"])
    with col2:
        ac_type = slt.selectbox("Select AC Type", ["AC", "Non-AC"])

    # Rating dropdown and Start Time, Fare Range
    col4, col5, col6 = slt.columns(3)
    with col4:
        rating_range = slt.selectbox("Select Rating Range", ["1 to 2", "2 to 3", "3 to 4", "4 to 5"])
    with col5:
        start_time = slt.time_input("Select Starting Time", value=None)
    with col6:
        fare_range = slt.selectbox("Select Bus Fare Range", ["50-1000", "1000-2000", "2000 and above"])

    # Get bus details based on selected filters
    bus_details = get_bus_details(state, route, seat_type, ac_type, rating_range, fare_range, start_time)

    # Display the results
    if bus_details.empty:
        slt.write("No buses found matching your criteria.")
    else:
        slt.dataframe(bus_details)