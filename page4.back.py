import streamlit as st
import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime
from charts import employee_pay_chart_grade_edited
from calculations import market_rates_calculations

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

def initialize_session_state():
    """Initialize session state variables."""
    if "working_data" not in st.session_state:
        # Load original data
        original_data = load_data("data_csv/grade_first_cut.csv")
        
        # Calculate metrics on original data
        if original_data is not None:
            working_data = calculate_metrics(original_data)
        else:
            working_data = pd.DataFrame()
        
        # Persist in session state
        st.session_state.original_data = original_data
        st.session_state.working_data = working_data
        
        # Immediately save working data to edited CSV
        if not working_data.empty:
            working_data.to_csv("data_csv/grade_edited.csv", index=False)

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
        
        return df

    except Exception as e:
        st.error(f"An error occurred while resetting last change: {e}")
        return df

def reset_all_changes():
    """Reset all changes to original data."""
    try:
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
            os.remove("data_csv/edit_log.csv")
        
        return df

    except Exception as e:
        st.error(f"An error occurred while resetting all changes: {e}")
        return None

def show():
    """Main function to display the page for calibrating pay ranges."""
    # Ensure session state is initialized
    initialize_session_state()

    st.markdown("<h2 style='color: #4A90E2;'>Calibrate Pay Ranges</h2>", unsafe_allow_html=True)
    
    # Display grid
    st.write("### Pay Ranges:")
    df_display = st.session_state.working_data.copy()
    df_display['Grade'] = df_display['Grade'].astype(int)
    for col in ['Range Min', 'Range Mid', 'Range Max']:
        df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")
    for col in ['Range Spread', 'Mid Point Differential', 'Range Overlap']:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else '')
    
    st.dataframe(df_display.sort_values(by='Grade', ascending=False), use_container_width=True, hide_index=True)

    # Layout for parameter selection
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    with col1:
        parameter = st.radio(
            "Select Parameter to Modify:",
            ["Range Mid", "Range Spread"],
            horizontal=True
        )

    grade_options = st.session_state.working_data['Grade'].unique()
    with col3:
        grade = st.selectbox("Select Grade", grade_options)

    grade_data = st.session_state.working_data[st.session_state.working_data['Grade'] == grade]
    current_value = grade_data[parameter].iloc[0] if not grade_data.empty else 0.0

    with col4:
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
                step=0.1,
                format="%.2f"
            )

    # Buttons for update and reset
    button_row = st.columns([2, 1, 1, 1, 2])
    
    # Update Button
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
            st.rerun()

    # Reset All Changes
    with button_row[3]:
        if st.button("Reset All Changes", use_container_width=True):
            # Use reset_all_changes() and update session state
            reset_data = reset_all_changes()
            if reset_data is not None:
                st.session_state.working_data = reset_data
                st.success("All changes have been reset to original values.")
                st.rerun()

    # Reset Last Change
    with button_row[4]:
        if st.button("Reset Last Change", use_container_width=True):
            st.session_state.working_data = reset_last_change(st.session_state.working_data)
            # Save the updated data 
            st.session_state.working_data.to_csv("data_csv/grade_edited.csv", index=False)
            st.rerun()

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