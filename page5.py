import streamlit as st
import pandas as pd
import os
from datetime import datetime
from calculations import market_rates_calculations
from charts import employee_pay_chart_pay_range_final

def initialize_data():
  # Load the original data from grade_edited.csv
  df_original = pd.read_csv('data_csv/grade_edited.csv')
  # Ensure columns are numeric
  for col in ['Range Min', 'Range Mid', 'Range Max']:
      df_original[col] = pd.to_numeric(df_original[col], errors='coerce')
  # Ensure 'Grade' is integer
  df_original['Grade'] = df_original['Grade'].astype(int)
  # Ensure percentage columns are numeric
  for col in ['Range Spread', 'Mid Point Differential', 'Range Overlap']:
      df_original[col] = pd.to_numeric(df_original[col], errors='coerce')

  # Initialize pay_range_final.csv if it doesn't exist
  if not os.path.exists('data_csv/pay_range_final.csv'):
      df_original.to_csv('data_csv/pay_range_final.csv', index=False)

  return df_original

def load_user_inputs():
  # Load user inputs from CSV if it exists
  if os.path.exists('aging.csv'):
      user_inputs = pd.read_csv('data_csv/aging.csv')
      return user_inputs.iloc[0]['Annual'], user_inputs.iloc[0]['No_of_months']
  else:
      return 4.0, 6

def save_user_inputs(annual, months):
  # Save user inputs to CSV
  user_inputs = pd.DataFrame({'Annual': [annual], 'No_of_months': [months]})
  user_inputs.to_csv('data_csv/aging.csv', index=False)

def apply_aging(df, annual_rate, months):
  try:
      # Calculate aged values
      annual_factor = annual_rate / 100  # Convert percentage to decimal
      monthly_factor = months / 12  # Convert months to year fraction
      factor = 1 + (annual_factor * monthly_factor)

      df['Range Min'] = df['Range Min'] * factor
      df['Range Mid'] = df['Range Mid'] * factor
      df['Range Max'] = df['Range Max'] * factor

      # Round the values to integers
      df['Range Min'] = df['Range Min'].round(0).astype(int)
      df['Range Mid'] = df['Range Mid'].round(0).astype(int)
      df['Range Max'] = df['Range Max'].round(0).astype(int)
      return df
  except Exception as e:
      st.error(f"An error occurred during aging: {e}")
      return df

def show():
  st.markdown("""
      <h2 style='color: #4A90E2;'>Age Your Pay Ranges</h2>
      """, unsafe_allow_html=True)

  # Initialize data
  df_original = initialize_data()

  # Load the current data from pay_range_final.csv
  df_current = pd.read_csv('data_csv/pay_range_final.csv')

  # Load user inputs
  annual_default, months_default = load_user_inputs()

  # Initialize session state variables if not already present
  if 'Annual' not in st.session_state:
      st.session_state['Annual'] = annual_default
  if 'No_of_months' not in st.session_state:
      st.session_state['No_of_months'] = months_default
  if 'age_applied' not in st.session_state:
      st.session_state['age_applied'] = False
  if 'working_data' not in st.session_state:
      st.session_state['working_data'] = df_current.copy()

  # Question with radio buttons at the top
  age_choice = st.radio(
      "Do you want to age the data?",
      options=['Yes - That\'s a good idea', "No - I'm fine"], horizontal=True,
      key='age_choice'
  )

  # If aging is selected
  if age_choice == 'Yes - That\'s a good idea':
      st.write("Aging Parameters")

      # Define the columns for layout
      col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

      # Create input widgets
      with col1:
          age_input1 = st.number_input(
              "Annual (%)",
              min_value=1.0,  # Prevent decrementing below 1.0
              step=0.1,
              format="%.1f",
              key='Annual'
          )
      with col2:
          age_input2 = st.number_input(
              "No. of months",
              min_value=1,    # Prevent decrementing below 1
              step=1,
              key='No_of_months'
          )
      with col3:
          age_button = st.button("Age")

      # Initialize reset_button to avoid UnboundLocalError
      reset_button = False
      # Show Reset button only if Age has been applied
      if st.session_state['age_applied']:
          with col4:
              reset_button = st.button("Reset")

      if age_button:
          df_aged = apply_aging(st.session_state['working_data'].copy(), st.session_state['Annual'], st.session_state['No_of_months'])
          df_aged.to_csv('data_csv/pay_range_final.csv', index=False)
          save_user_inputs(st.session_state['Annual'], st.session_state['No_of_months'])
          st.session_state['age_applied'] = True
          st.session_state['working_data'] = df_aged  # Update session state with aged data
          st.success("Pay ranges have been aged.")
          st.rerun()  # Rerun the app to update the UI

      if st.session_state['age_applied'] and reset_button:
          # Reset user inputs to default values
          df_original.to_csv('data_csv/pay_range_final.csv', index=False)
          st.session_state['age_applied'] = False
          st.session_state['working_data'] = df_original  # Reset session state to original data
          st.rerun()  # Rerun the app to update the UI

  # Reset all aging if "No - I'm fine" is selected
  if age_choice == "No - I'm fine":
      # Reset the data to its original state
      df_original.to_csv('data_csv/pay_range_final.csv', index=False)
      # Clear session state variables related to aging
      for key in ['Annual', 'No_of_months', 'age_applied', 'working_data']:
          if key in st.session_state:
              del st.session_state[key]
      st.session_state['working_data'] = df_original.copy()  # Reinitialize working data
      st.success("Aging has been reset to original values.")
      # Do not rerun here to ensure the page components are reloaded correctly

  # Display the DataFrame using Streamlit's native display
  st.write("### Pay Ranges:")

  # Format columns
  df_display = st.session_state['working_data']

  # Ensure 'Grade' column is integer
  df_display['Grade'] = df_display['Grade'].astype(int)

  # Sort DataFrame by Grade in descending order
  df_display = df_display.sort_values(by='Grade', ascending=False)

  # Format currency columns with commas
  currency_cols = ['Range Min', 'Range Mid', 'Range Max']
  for col in currency_cols:
      df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else '')

  # Format percentage columns with '%' symbol
  percentage_cols = ['Range Spread', 'Mid Point Differential', 'Range Overlap']
  for col in percentage_cols:
      df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else '')

  # Replace NaN or None values with empty strings
  df_display = df_display.fillna('')

  # Display the formatted DataFrame
  st.dataframe(
      df_display,
      use_container_width=True,
      hide_index=True
  )

  st.write("")
  
  
  # Download section
  col_reset_all, col_download = st.columns([1, 1])
#   with col_reset_all:
#       reset_all_button = st.button("Reset All")
  with col_download:
      csv_data = df_display.to_csv(index=False).encode('utf-8')
      today_str = datetime.today().strftime('%d%b%y')
      download_filename = f"Final_Pay_Range_{today_str}.csv"
      download_button = st.download_button(
          label="🔽 Download Pay Ranges",
          data=csv_data,
          file_name=download_filename,
          mime='text/csv',
          key="page5_download_payrange_button"
      )

  if download_button:
      st.success("👍Congrats for getting closer to pay transparency goals")
  
  st.write("")        
  st.write("")

  # Charts section
  with st.expander("Analytics"):
      st.write("Your Pay Ranges")
      try:
          fig = market_rates_calculations.create_salary_structure_bar_chart(
              st.session_state['working_data']
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
              fig = employee_pay_chart_pay_range_final.create_chart(
                  user_data, 
                  st.session_state['working_data']
              )
              st.plotly_chart(fig, use_container_width=True)
  except FileNotFoundError:
      st.warning("User data file not found. Employee distribution chart will not be displayed.")

  # Navigation
  col1, col2, col3, col4, col5 = st.columns(5)
  with col4:
      if st.button("← Previous"):
          # Reset specific session state variables when navigating back to page 4
          for key in ['Annual', 'No_of_months', 'age_applied', 'working_data']:
              if key in st.session_state:
                  del st.session_state[key]
          st.session_state.page = 'page4'
          st.rerun()
  with col5:
      if st.button("Next →"):
          st.session_state.page = 'page6'
          st.rerun()

def main():
  show()

if __name__ == "__main__":
  main()