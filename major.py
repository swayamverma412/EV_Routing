import streamlit as st
import osmnx as ox
import networkx as nx
import pandas as pd
from app import shortest_path_with_constraints
from end import find_nearest_charging_station

# Load the graph (assuming you have saved it as 'delhi_ev_graph.graphml')
G = ox.load_graphml('delhi_ev_graph.graphml')

# Define a function to compute the battery range gained by charging for a specified time
def compute_battery_range(charging_time):
    # Compute the battery range gained by charging for the specified time
    battery_range_gained = charging_time * 60  # Assume 60 km of range gained per hour of charging
    return battery_range_gained

# Streamlit app layout
st.title("EV Routing Application")

# Input form
start_address = st.text_input("Enter starting address:", value="New Delhi, India")
end_address = st.text_input("Enter destination address:", value="Gurugram, India")
battery_charge = st.slider("Select current battery charge (in kilometers):", 0, 500, 0)
charging_time = st.slider("Select charging time (in hours):", 0, 12, 0)

if st.button("Plan Route"):
    if start_address and end_address:
        # Geocode the addresses to get coordinates
        start_location = ox.geocode(start_address)
        end_location = ox.geocode(end_address)

        # Find the nearest nodes to the starting and ending points
        start_node = ox.distance.nearest_nodes(G, X=[start_location[1]], Y=[start_location[0]], return_dist=False)[0]
        end_node = ox.distance.nearest_nodes(G, X=[end_location[1]], Y=[end_location[0]], return_dist=False)[0]

        # Compute the battery range gained by charging for the specified time
        battery_range_gained = compute_battery_range(charging_time)

        # Compute the battery range considering the current battery charge and charging time
        battery_range = battery_charge + battery_range_gained

        # Compute the shortest path using Dijkstra's algorithm based on distance and battery constraints
        shortest_path = shortest_path_with_constraints(G, start_node, end_node, battery_range, charging_time, weight='length')
        shortest_path_distance = nx.shortest_path_length(G, source=start_node, target=end_node, weight='length')

        # Display the route information
        st.subheader("Route Information")
        st.write(f"Starting Address: {start_address}")
        st.write(f"Destination Address: {end_address}")
        st.write(f"Shortest path: {shortest_path}")
        st.write(f"Total distance: {shortest_path_distance:.2f} km")

        # Visualize the route on a map
        st.subheader("Route Map")
        fig, ax = ox.plot_graph_route(G, shortest_path, route_linewidth=6, node_size=0, bgcolor='k', edge_color='w', edge_linewidth=0.5, show=False, close=False)
        st.pyplot(fig)

        # Check if the battery charge is insufficient to reach the destination
        if shortest_path_distance > battery_range:
            # Find the nearest charging station to the destination
            nearest_charging_station = find_nearest_charging_station(G, end_node)
            st.subheader("Charging Station Information")
            st.write(f"Battery charge insufficient to reach the destination.")
            st.write(f"Nearest charging station: {nearest_charging_station}")
