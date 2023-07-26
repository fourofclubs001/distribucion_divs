import streamlit as st
import pandas as pd
import networkx as nx
import numpy as np

def read_csv_file(file_data):

    csv_data = file_data.iloc[:,2:9]

    return csv_data

def csv_to_digraph(csv_data, max_solapamiento, max_turnos):

    G = nx.DiGraph()

    for _, row in csv_data.iterrows():

        div_name = row["Div"]
        div_capacity = np.sum(row == "Puedo")
        G.add_edge("s", div_name, capacity=min(div_capacity, max_turnos))

        for column_name in row.index:

            if(column_name != "Div" and row[column_name] == "Puedo"):

                G.add_edge(div_name, column_name, capacity=1)

    for column_name in csv_data.columns:

        G.add_edge(column_name, "t", capacity=max_solapamiento)

    return G

def solve_assignation(G):

    flow_value, flow_dict = nx.maximum_flow(G, "s", "t")

    return flow_dict

def solution_to_df(csv_data, flow_dict):

    divs = csv_data["Div"]

    solution = {}
    solution["Div"] = divs

    for column in csv_data.columns:

        if(column != "Div"): solution[column] = np.repeat("", csv_data.shape[0])

    for div_idx, div in enumerate(divs):

        for column, value in flow_dict[div].items():

            if value == 1: solution[column][div_idx] = 'P'

    return pd.DataFrame(solution)

def calculate_distribution(file_data, max_solapamiento, max_turnos):

    csv_data = read_csv_file(file_data)
    G = csv_to_digraph(csv_data, max_solapamiento, max_turnos)
    flow_dict = solve_assignation(G)
    return solution_to_df(csv_data, flow_dict)

def mix_dataframe_rows(df):
    mixed_df = df.sample(frac=1).reset_index(drop=True)
    return mixed_df

refresh = False

st.title("Distribución Divulgadores")

# Allow the user to upload a CSV file
uploaded_file = st.file_uploader("Subir archivo CSV", type=["csv"])

# Check if a file has been uploaded
if uploaded_file is not None:

    left_column, right_column = st.columns([0.3,0.7])

    with left_column:

        # Sliders
        max_solapamiento = st.slider('maximo solapamiento', 1, 10)
        max_turnos = st.slider('maximos turnos', 1, 10)

        refresh = st.button('nueva distribución')

    with right_column:

        # Read the CSV data into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Mix dataset columns
        if(refresh): df = mix_dataframe_rows(df)

        # Calculate solution
        solution = calculate_distribution(df, max_solapamiento, max_turnos)

        # Reorder by name
        solution_ordered = solution.sort_values(by='Div', ascending=True)
        
        solution_ordered.reset_index(inplace=True)
        solution_ordered.drop('index', axis=1, inplace=True)

        # Display Solution
        st.table(solution_ordered)

        # Download button
        st.download_button(
            "Descargar",
            solution_ordered.to_csv(index=False).encode('utf-8'),
            "distribucion_divs.csv",
            "text/csv",
        )
