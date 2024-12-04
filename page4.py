import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import shutil
from datetime import datetime
from charts import employee_pay_chart_grade_edited
from calculations import market_rates_calculations
import time

# Function to calculate the metrics
def calculate_metrics(df):
    """
    Calculates Mid Point Differential and Range Overlap for the salary grades.
    Assumes grades are sorted in descending order.
    """
    # Sort dataframe by Grade in descending order
    df_sorted = df.sort_values('Grade', ascending=False).reset_index(drop=True)
    
    # Initialize new columns
    df_sorted['Mid Point Differential'] = np.nan
    df_sorted['Range Overlap'] = np.nan
    df_sorted['Range Min'] = np.nan  # To be recalculated
    df_sorted['Range Max'] = np.nan  # To be recalculated

    # Recalculate Range Min and Range Max based on the provided formulas
    df_sorted['Range Min'] = df_sorted['Range Mid'] - (df_sorted['Range Mid'] * df_sorted['Range Spread'] / 200)
    df_sorted['Range Max'] = df_sorted['Range Min'] * (1 + df_sorted['Range Spread'] / 100)

    # Mid Point Differential: Exclude the lowest grade
    # Calculate percentage difference between consecutive mid points
    df_sorted['Mid Point Differential'][:-1] = (
        (df_sorted['Range Mid'][:-1] / df_sorted['Range Mid'][1:].values) - 1
    ) * 100

    # Range Overlap: Exclude the highest grade
    # Calculate overlap percentage between consecutive grades
    df_sorted['Range Overlap'][1:] = (
        (df_sorted['Range Max'][1:].values - df_sorted['Range Min'][:-1]) /
        (df_sorted['Range Max'][1:].values - df_sorted['Range Min'][1:].values)
    ) * 100

    return df_sorted

# Load the data from CSV
def load_data(file_path):
    """Load data from the provided CSV file and return as DataFrame."""
    try:
        df = pd.read_csv(file_path)
        df["Grade"] = df["Grade"].astype(int)
        numeric_cols = ["Range Min", "Range Mid", "Range Max", "Range Spread", "Mid Point Differential", "Range Overlap"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error while loading data: {e}")
        return None

# Initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    if os.path.exists("data_csv/grade_edited.csv"):
            # Load the edited data from grade_edited.csv
            working_data = load_data("data_csv/grade_edited.csv")
    else:
            # If the edited file doesn't exist, load original data from grade_first_cut.csv
            original_data = load_data("data_csv/grade_first_cut.csv")
            if original_data is not None:
                # Calculate metrics on the original data
                working_data = calculate_metrics(original_data)
            else:
                # If data couldn't be loaded, return an empty dataframe
                working_data = pd.DataFrame()

            # Immediately save working data to edited CSV if it's not empty
            if not working_data.empty:
                working_data.to_csv("data_csv/grade_edited.csv", index=False)

    # Persist in session state
    st.session_state.working_data = working_data
        
    # Optionally, you can also store the original data if needed
    st.session_state.original_data = working_data if "original_data" not in st.session_state else st.session_state.original_data


# Save edits to log
def save_edit_log(grade, parameter, current_value, new_value):
    """Append edit logs while maintaining a maximum of 100 records."""
    edit_log_path = 'data_csv/edit_log.csv'
    new_record = pd.DataFrame({
        'Grade': [grade],
        'Parameter': [parameter],
        'Current Value': [current_value],
        'Updated Value': [new_value],
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    
    # Load existing edit log or create a new DataFrame
    if os.path.exists(edit_log_path):
        edit_log = pd.read_csv(edit_log_path)
    else:
        edit_log = pd.DataFrame(columns=new_record.columns)
    
    # Append new record and retain the last 100 rows
    edit_log = pd.concat([edit_log, new_record]).tail(100)
    edit_log.to_csv(edit_log_path, index=False)

# Reset the last change
def reset_last_change(df):
    """Reverse the most recent change from the edit log."""
    try:
        edit_log_path = "data_csv/edit_log.csv"
        if not os.path.exists(edit_log_path):
            st.warning("Edit log file not found. No changes to reset.")
            return df
        
        edit_log = pd.read_csv(edit_log_path)
        if edit_log.empty:
            st.warning("No changes to reset.")
            return df
        
        # Get the last change
        last_change = edit_log.iloc[-1]
        grade = last_change['Grade']
        parameter = last_change['Parameter']
        current_value = last_change['Current Value']
        
        # Find the grade in the current data
        if grade in df['Grade'].values:
            current_index = df[df['Grade'] == grade].index[0]
            
            # Revert the change
            df.loc[current_index, parameter] = current_value
            
            # Recalculate metrics after reverting
            df = calculate_metrics(df)
            
            # Save updated data
            df.to_csv("data_csv/grade_edited.csv", index=False)
            
            # Remove the last log entry
            edit_log = edit_log[:-1]
            edit_log.to_csv(edit_log_path, index=False)
            
            st.success(f"Reverted the last change for Grade {grade}, {parameter}.")
        else:
            st.error(f"Grade {grade} not found in data. Cannot reset.")
        time.sleep(1)
        return df

    except Exception as e:
        st.error(f"An error occurred while resetting last change: {e}")
        return df

# Reset all changes
def reset_all_changes():
    """Reset all changes to original data."""
    try:
        # Define the edit log path
        edit_log_path = "data_csv/edit_log.csv"

        # Verify first-cut data file exists
        if not os.path.exists("data_csv/grade_first_cut.csv"):
            st.error("First-cut data file ('grade_first_cut.csv') not found. Cannot reset.")
            return None
        
        # Load first-cut data
        df = pd.read_csv("data_csv/grade_first_cut.csv")
        
        # Recalculate metrics
        df = calculate_metrics(df)
        
        # Save it as the current working data
        df.to_csv("data_csv/grade_edited.csv", index=False)
        
        # Clear the edit log
        if os.path.exists("data_csv/edit_log.csv"):
            with open(edit_log_path, "w") as file:
                # Write headers to keep file structure intact
                file.write("Grade,Parameter,Current Value,Updated Value,Timestamp\n")

        st.success("All changes have been reset to the original values, and the edit log has been cleared.")
        return df
       
    except Exception as e:
        st.error(f"An error occurred while resetting all changes: {e}")
        return None

# Main function to display the page
def show():
    """Main function to display the page for calibrating pay ranges."""
    # Ensure session state is initialized
    initialize_session_state()

    # Title
    st.markdown("<h2 style='color: #4A90E2;'>Calibrate Pay Ranges</h2>", unsafe_allow_html=True)


    # Layout for radio buttons and buttons - placed at the top
    button_row = st.columns([1, 1, 1, 1, 1, 1])

    # Radio Button for parameter selection (at the top)
    with button_row[0]:
        parameter = st.radio(
            "Select Parameter to Modify:",
            ["Range Mid", "Range Spread"],
            horizontal=False
        )

    # Select Grade (at the top)
    grade_options = st.session_state.working_data['Grade'].unique()
    with button_row[0]:
        grade = st.selectbox("Select Grade", grade_options)

    # Get current value for the selected grade and parameter
    grade_data = st.session_state.working_data[st.session_state.working_data['Grade'] == grade]
    current_value = grade_data[parameter].iloc[0] if not grade_data.empty else 0.0

    # Input for new value of the selected parameter
    with button_row[1]:
        if parameter == "Range Mid":
            new_value = st.number_input(
                f"New {parameter}",
                value=int(current_value) if pd.notnull(current_value) else 0,
                step=1,
                format="%d"
            )
        else:  # Range Spread
            new_value = st.number_input(
                f"New {parameter}",
                value=float(current_value) if pd.notnull(current_value) else 0.0,
                step=.5,
                format="%.2f"
            )

    # Buttons for update, reset, and reset all changes
    with button_row[2]:
        if st.button("Update", use_container_width=True, key="update_button"):
            current_index = st.session_state.working_data[st.session_state.working_data['Grade'] == grade].index[0]
            old_value = st.session_state.working_data.loc[current_index, parameter]

            # Update the working data with new value
            st.session_state.working_data.loc[current_index, parameter] = new_value
            
            # Recalculate metrics after update
            st.session_state.working_data = calculate_metrics(st.session_state.working_data)
            
            # Save change to edit log
            save_edit_log(grade, parameter, old_value, new_value)
            
            # Save updated data to file
            st.session_state.working_data.to_csv("data_csv/grade_edited.csv", index=False)
            
            # Show success message and rerun to refresh
            st.success(f"Updated {parameter} for Grade {grade}.")
            # Add a 1-second delay
            time.sleep(1)
            st.rerun

    # Check the edit log for the number of records
    edit_log_path = "data_csv/edit_log.csv"
    edit_log_exists = os.path.exists(edit_log_path)

    if edit_log_exists:
        edit_log = pd.read_csv(edit_log_path)
        edit_log_count = len(edit_log)  # Total rows in the file
    else:
        edit_log_count = 0        

    with button_row[4]:
      if edit_log_count >= 2: # Reset all button should be visible only from the second updates 
        if st.button("Reset All", use_container_width=True):
            # Use reset_all_changes() and update session state
            reset_data = reset_all_changes()
            if reset_data is not None:
                st.session_state.working_data = reset_data
                # st.success("All changes have been reset to original values.")
                st.rerun()

    # Reset Last Change
    with button_row[3]:
      if edit_log_count >= 1: # Reset button should be visible after 1 update
        if st.button("Reset", use_container_width=True):
            st.session_state.working_data = reset_last_change(st.session_state.working_data)
            # Save the updated data 
            st.session_state.working_data.to_csv("data_csv/grade_edited.csv", index=False)
            st.rerun()

    # Display grid after controls
    st.write("### Pay Ranges:")
    df_display = st.session_state.working_data.copy()
    df_display['Grade'] = df_display['Grade'].astype(int)
    for col in ['Range Min', 'Range Mid', 'Range Max']:
        df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")
    for col in ['Range Spread', 'Mid Point Differential', 'Range Overlap']:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else '')
    
    st.dataframe(df_display.sort_values(by='Grade', ascending=False), use_container_width=True, hide_index=True)


 # Charts section
    with st.expander("Analytics"):
            st.write("Your Pay Ranges")
            try:
                fig = market_rates_calculations.create_salary_structure_bar_chart(
                    st.session_state.working_data
                )
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating salary structure chart: {str(e)}")

        # Employee Distribution Chart
    try:
            user_data = pd.read_csv('data_csv/user_loaded_data.csv')
            if 'Base Pay' in user_data.columns:
                with st.expander("Employee Distribution"):
                    fig = employee_pay_chart_grade_edited.create_chart(
                        user_data, 
                        st.session_state.working_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
    except FileNotFoundError:
            st.warning("User data file not found. Employee distribution chart will not be displayed.")

# Navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col4:
            if st.button("← Previous"):
                st.session_state.page = 'page3'
                st.rerun()
    with col5:
            if st.button("Next →"):
                st.session_state.page = 'page5'
                st.rerun()

def main():
    show()

if __name__ == "__main__":
    main()

# Run the application
if __name__ == "__main__":
    show()
