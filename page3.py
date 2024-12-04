import streamlit as st
import pandas as pd
import os
from calculations import market_rates_calculations
from calculations import employee_pay_calculations
from calculations import combination_strategy_calculations
from charts import employee_pay_chart

def get_selected_approach():
    try:
        if os.path.exists('data_csv/selected_option.csv'):
            df = pd.read_csv('data_csv/selected_option.csv')
            return df['selected_approach'].iloc[0]
    except Exception as e:
        st.error(f"Error reading selection: {e}")
    return None

def get_imported_data():
    try:
        if os.path.exists('data_csv/user_loaded_data.csv'):
            return pd.read_csv('data_csv/user_loaded_data.csv')
    except Exception as e:
        st.error(f"Error reading imported data: {e}")
    return None

def perform_calculation(selected_option, df):
    """Performs calculations based on the selected option."""
    try:
        if selected_option == "Market rates of jobs to create pay ranges":
            pay_ranges_df = market_rates_calculations.calculate(df)
        elif selected_option == "Pay data of existing employees to build pay ranges":
            pay_ranges_df = employee_pay_calculations.calculate(df)
        elif selected_option == "A combination strategy as it's well aligned with my organization":
            pay_ranges_df = combination_strategy_calculations.calculate(df)
        else:
            pay_ranges_df = pd.DataFrame()
            st.warning("Unsupported calculation option selected.")
        return pay_ranges_df
    except Exception as e:
        st.error(f"Error in performing calculation: {e}")
        return pd.DataFrame()

def show():
    """Main logic for displaying and processing data."""
    st.markdown("<h2 style='color: #4A90E2;'>Pay Ranges</h2>", unsafe_allow_html=True)

    # Get selected approach and imported data from files
    selected_option = get_selected_approach()
    df = get_imported_data()

    # Debug information
    # st.write("Debug Info:")
    st.write(f"**Selected approach:** {selected_option}")
    # st.write(f"Data loaded: {'Yes' if df is not None else 'No'}")
    # if df is not None:
        # st.write(f"Columns in loaded data: {list(df.columns)}")

    # if df is None:
    #     st.error("No data found. Please upload data in the previous step.")
    #     if st.button("← Go Back"):
    #         st.session_state.page = 'page2'
    #         st.rerun()
    #     return

    # if selected_option is None:
    #     st.error("No approach selected. Please go back and select an approach.")
    #     if st.button("← Go Back"):
    #         st.session_state.page = 'page1'
    #         st.rerun()
    #     return

    # st.write(f"**Basis of computation:** {selected_option}")

    # Perform calculations
    pay_ranges_df = perform_calculation(selected_option, df)

    if not pay_ranges_df.empty:
        # Format data for display
        pay_ranges_df_display = pay_ranges_df.copy()
        pay_ranges_df_display['Range Spread'] = pay_ranges_df_display['Range Spread'].apply(lambda x: f"{x:.1f}%")
        pay_ranges_df_display['Mid Point Differential'] = pay_ranges_df_display['Mid Point Differential'].apply(
            lambda x: f"{x:.1f}%" if pd.notnull(x) else ''
        )
        pay_ranges_df_display['Range Overlap'] = pay_ranges_df_display['Range Overlap'].apply(
            lambda x: f"{x:.1f}%" if pd.notnull(x) else ''
        )
        pay_ranges_df_display['Range Min'] = pay_ranges_df_display['Range Min'].apply(lambda x: f"{x:,.0f}")
        pay_ranges_df_display['Range Mid'] = pay_ranges_df_display['Range Mid'].apply(lambda x: f"{x:,.0f}")
        pay_ranges_df_display['Range Max'] = pay_ranges_df_display['Range Max'].apply(lambda x: f"{x:,.0f}")

        # Save and download options
        os.makedirs('data_csv', exist_ok=True)
        pay_ranges_df.to_csv("data_csv/grade_first_cut.csv", index=False)
        pay_ranges_df.to_csv("data_csv/grade_edited.csv", index=False)

        st.dataframe(pay_ranges_df_display, hide_index=True)

        # Analytics expander
        with st.expander("Analytics"):
            fig = market_rates_calculations.create_salary_structure_bar_chart(pay_ranges_df)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        # Employee Distribution (if 'Base Pay' exists)
        if 'Base Pay' in df.columns:
            with st.expander("Employee Distribution"):
                fig = employee_pay_chart.create_chart(df, pay_ranges_df)
                st.plotly_chart(fig, use_container_width=True)

        st.session_state.pay_ranges_df = pay_ranges_df
    else:
        st.error("No valid data to display pay ranges. Please check the uploaded file.")


     # Load data from 'grade_edited.csv' for current session state
    if "working_data" not in st.session_state:
        df = ('data_csv/grade_first_cut.csv')
        if df is None:
            st.stop()  # Stop execution if data couldn't be loaded
            initialize_session_state(df)
   
   
    # Navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col5:
        if st.button("Next →", key="next_button"):
            # Load data from 'grade_edited.csv' for resetting session state
            df = pd.read_csv('data_csv/grade_edited.csv')  # Use your loading function here
            if df is None:
                st.error("Error loading 'grade_edited.csv'.")
                st.stop()  # Stop execution if data couldn't be loaded

            # Initialize session state with the loaded data
                initialize_session_state(df, is_reset=True)  # Reset session state

            # Set the page navigation target to 'page4'
            st.session_state.page = 'page4'  # Navigate to the next page
            st.rerun()  # Rerun the app to load the next page with fresh data

    
    with col4:
        if st.button("← Previous"):
            st.session_state.page = 'page2'
            st.rerun()

def main():
    show()


if __name__ == "__main__":
    main()
