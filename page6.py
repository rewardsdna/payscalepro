import streamlit as st
import pandas as pd
import datetime 
from charts import employee_pay_chart_pay_range_final
from calculations import dashboard_calculations_1
from calculations import dashboard_calculations_2_3
from calculations import market_rates_calculations
from charts import gender_pay_gap


def show():
    st.markdown("""
        <h2 style='color: #4A90E2;'>💹Comp Dashboard</h2>
    """, unsafe_allow_html=True)

    # Define file paths
    pay_range_file = "data_csv/pay_range_final.csv"
    user_data_file = "data_csv/user_loaded_data.csv"

    # Load data
    try:
        user_loaded_data = pd.read_csv(user_data_file, na_values=["NA", ""])
        working_data = pd.read_csv(pay_range_file)
    except Exception as e:
        st.error(f"Error loading data files: {e}")
        return

    # Perform calculations
    try:
        results_1 = dashboard_calculations_1.calculate_pay_metrics(pay_range_file, user_data_file)
    except Exception as e:
        st.error(f"Error calculating metrics (Overview): {e}")
        return

    # Display Overview section
    with st.expander("Pay Range Overview"):
        st.write("Get a high level view of pay range")
        #st.subheader("High-Level Metrics")
        try:
            cols = st.columns(5)
            cols[0].metric(label="Grades", value=results_1.get("grade_count", "N/A"))
            cols[1].metric(label="Jobs", value=results_1.get("job_count", "N/A"))
            cols[2].metric(label="Avg. Mid Pnt. Diff.", value=results_1.get("avg_midpoint_differential", "N/A"))
            cols[3].metric(label="Avg. Overlap", value=results_1.get("avg_range_overlap", "N/A"))
            cols[4].metric(label="Avg. Spread", value=results_1.get("avg_range_spread", "N/A"))
            
            
            # cols[3].metric(label="Avg. Base Pay", value=f"${results_1.get('avg_base_pay', 'N/A')}")
            # cols[4].metric(label="Median Base Pay", value=f"${results_1.get('med_base_pay', 'N/A')}")
        except Exception as e:
            st.error(f"Employee Pay Range Distribution is not available for the selected approach: {e}")

    # Charts section
    with st.expander("Pay Structure Visualization"):
        st.write("See pay range progression")
        try:
            fig = market_rates_calculations.create_salary_structure_bar_chart(working_data)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating salary structure chart: {e}")

    # Employee Distribution Chart
    with st.expander("Employees Pay Range Distribution"):
        st.write("Get a high level view of pay range")
        try:
            fig = employee_pay_chart_pay_range_final.create_chart(user_loaded_data, working_data)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Employee Pay Range Distribution is not available for the selected approach: {e}")

    
    # Deep Dive Metrics
    with st.expander("Deep Dive Metrics"):
        st.write("Understand employee pay distribution")
        try:
            # Normalize column names and ensure numeric conversion
            user_loaded_data.columns = user_loaded_data.columns.str.strip()
            user_loaded_data['Base Pay'] = pd.to_numeric(user_loaded_data['Base Pay'], errors='coerce')

            # Perform calculations
            results_2_3 = dashboard_calculations_2_3.calculate_pay_metrics(pay_range_file, user_data_file)

            # Pay Distribution Overview metrics
            cols = st.columns(5)
            cols[0].metric(label="Head Count", value=f"{int(results_2_3.get('employee_count', 0)):,}")
            cols[1].metric(label="Within Range", value=f"{int(results_2_3.get("green_circled", 0)):,}")   
            cols[2].metric(label="Within Range %", value=f"{float(results_2_3.get('within_range_pct', 0)) * 100:.0f}%")
            cols[4].metric(label="Outliers %", value=f"{float(results_2_3.get('outliers_pct', 0)) * 100:.0f}%")
            cols[3].metric(label="Outliers", value=f"{int(results_2_3.get('outliers', 0)):,}")
            
            

            cols = st.columns(5)
            cols[0].metric(label="Below Min", value=f"{int(results_2_3.get('count_below_range_min', 0)):,}")
            # cols[2].metric(label="Above Max", value=f"{int(results_2_3.get('count_above_range_max', 0)):,}")
            cols[1].metric(label="Below Min %", value=f"{float(results_2_3.get('below_min_pct', 0)) * 100:.0f}%")
            # cols[3].metric(label="Above Max %", value=f"{float(results_2_3.get('above_max_pct', 0)) * 100:.0f}%")
            cols[2].metric(label="Delta to Min", value=f"{int(results_2_3.get('pay_gap_sum', 0)) / 1000:,.0f}K")
            cols[3].metric(label="Gap/Payroll", value=f"{float(results_2_3.get('paygap_payroll_pct', 0)) * 100:.0f}%")
            cols[4].metric(label="Delta from Max", value=f"{int(results_2_3.get('range_max_sum', 0))/ 1000:,.0f}K")

            
            cols = st.columns(5)
            cols[4].metric(label="P90/P10", value=f"{float(results_2_3.get('p90_p10', 0)) * 100:.0f}%")
            cols[1].metric(label="Avg. Base Pay", value=f"{float(results_2_3.get('avg_base_pay', 0)) / 1000:,.1f}K")
            cols[0].metric(label="Median Base Pay", value=f"{float(results_2_3.get('med_base_pay', 0)) / 1000:,.1f}K")
            cols[2].metric(label="P25", value=f"{float(results_2_3.get('percentile_25', 0)) / 1000:,.1f}K")
            cols[3].metric(label="P75", value=f"{float(results_2_3.get('percentile_75', 0)) / 1000:,.1f}K")

                   
            cols = st.columns(5) 
            cols[0].metric(label="Avg. Compa-Ratio", value=f"{float(results_2_3.get('avg_compa_ratio', 0)) * 100:.1f}%")
            cols[1].metric(label="Med. Compa-Ratio", value=f"{float(results_2_3.get('med_compa_ratio', 0)) * 100:.1f}%")
            cols[3].metric(label="Med. Range Pen.", value=f"{float(results_2_3.get('med_range_pen', 0)) * 100:.1f}%")
            cols[2].metric(label="Avg. Range Pen.", value=f"{float(results_2_3.get('avg_range_pen', 0)) * 100:.1f}%")
            cols[4].metric(label="Max. Range Pen.", value=f"{float(results_2_3.get('max_range_pen', 0)) * 100:.1f}%")

            # New metrics to be added.
            # Grade with lowest number of outliers
            # Grade with highest number of outliers
            # Grade with highest pay gap
            # Grade with lowest pay gap
            # Gender Ratio
            # Grade with higher female concentration 

            
        except Exception as e:
            st.error(f"Employee-specific metrics are available only for approaches 2 & 3: {e}")


     # Display Overview section
    with st.expander("Gender Pay Gap Analytics"):
        st.subheader("GPG Metrics")
        try:
            
             # Pay Gap Metrics to be moved to another dashboard session
            cols = st.columns(5) 
            cols[0].metric(label="Avg. Pay Gap", value=f"{float(results_2_3.get('avg_pay_gap', 0)) * 100:.1f}%")
            cols[1].metric(label="Avg. Male Pay", value=f"{float(results_2_3.get('avg_male_pay', 0)) / 1000:,.1f}K")
            cols[2].metric(label="Avg. Female Pay.", value=f"{float(results_2_3.get('avg_female_pay', 0)) / 1000:,.1f}K")
            cols[3].metric(label="Avg. Pay Gap $.", value=f"{float(results_2_3.get('avg_pay_gap_dollar', 0)) / 1000:,.1f}K")
            cols[4].metric(label="Lowest Gap Grade", value=f"{int(results_2_3.get('pay_gap_min_grade', 0)):,}")
            cols[0].metric(label="Med. Pay Gap", value=f"{float(results_2_3.get('med_pay_gap', 0)) * 100:.1f}%")
            cols[1].metric(label="Med. Male Pay", value=f"{float(results_2_3.get('med_male_pay', 0)) / 1000:,.1f}K")
            cols[2].metric(label="Med. Female Pay.", value=f"{float(results_2_3.get('med_female_pay', 0)) / 1000:,.1f}K")
            cols[3].metric(label="Med. Pay Gap $.", value=f"{float(results_2_3.get('med_pay_gap_dollar', 0)) / 1000:,.1f}K")
            cols[4].metric(label="highest Gap Grade", value=f"{int(results_2_3.get('pay_gap_max_grade', 0)):,}")
            # New metrics to be added.
            
            
            # cols[3].metric(label="Avg. Base Pay", value=f"${results_1.get('avg_base_pay', 'N/A')}")
            # cols[4].metric(label="Median Base Pay", value=f"${results_1.get('med_base_pay', 'N/A')}")
        except Exception as e:
            st.error(f"GPG Metrics are not available for the selected approach.")

    
    # Future Reference only
    # Charts section
    # with st.expander("GPG Visuzations"):
    #     st.write("Gender Pay Gap")
    #     try:
    #         fig = gender_pay_gap.avg_gender_pay_chart(user_loaded_data, pay_range_file)
    #         st.plotly_chart(fig, use_container_width=True)
    #     except Exception as e:
    #         st.error(f"GPG Metrics are not available for the selected approach")


    # Gender Pay Gap Charts
    with st.expander("GPG Visualizations"):
        st.write("Gender Pay Gap Visualizations")
        
        # Define the charts and their corresponding function calls
        charts = [
            ("Gender Ratio", gender_pay_gap.gender_ratio_chart, user_loaded_data),
            ("Average Base Pay Gap", gender_pay_gap.avg_base_pay_gap_chart, user_loaded_data),
            ("Median Base Pay Gap", gender_pay_gap.med_base_pay_gap_chart, user_loaded_data),
            ("Gender Pay Gap", gender_pay_gap.avg_gender_pay_chart, user_loaded_data, pay_range_file),
            ("Gender Representation across Grades", gender_pay_gap.gender_grade_count_chart, user_loaded_data)
        ]
        
        # Define the number of charts in each row (custom layout)
        row_layout = [
            3,  # First row: 3 chart
            1,  # Second row: 1 chart
            1   # Third row: 2 chart
        ]
        
        # Track the current chart index
        chart_index = 0
        
        # Create rows based on the layout
        for num_cols in row_layout:
            if chart_index >= len(charts):
                break  # Stop if no more charts are available
            
            # Create columns for the row
            cols = st.columns(num_cols)
            
            # Add charts to the columns
            for col in cols:
                if chart_index < len(charts):
                    title, chart_func, *args = charts[chart_index]
                    with col:
                        st.write(title)  # Display chart title
                        try:
                            # Call the corresponding chart function dynamically
                            fig = chart_func(*args)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"{title} chart can is not available for the selected approach.")
                    chart_index += 1



    st.write("")
    st.write("")
    st.write("")
    
    # Download - Formatted final_pay_ranges.csv
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        # Generate dynamic filename
            pay_range_df = pd.read_csv('data_csv/pay_range_final.csv')
            # Format integer columns with 1000 separation
            integer_columns = ['Grade', 'Range Min', 'Range Mid', 'Range Max']
            for col in integer_columns:
                pay_range_df[col] = pay_range_df[col].apply(lambda x: f'{x:,}')

            # Format percentage columns with 1 decimal place
            percentage_columns = ['Range Spread', 'Mid Point Differential', 'Range Overlap']
            for col in percentage_columns:
                pay_range_df[col] = pay_range_df[col].apply(lambda x: f'{x:.1f}%')
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            file_name = f"Pay Range {current_date}.csv"
        
            # Function to handle download click
            if 'download_clicked' not in st.session_state:
                st.session_state['download_clicked'] = False

            def on_download_click():
                st.session_state['download_clicked'] = True

            st.download_button(
                label="🔽 Download Pay Ranges", 
                data = pay_range_df.to_csv(index=False).encode('utf-8'),
                file_name=file_name,
                mime="text/csv",
                key="page6_dashboard_Payrange_download_button",  # Fixed typo in key
                on_click=on_download_click,  # Call the function on button click
                )
            # Check if the download button was clicked and reset the state
            if st.session_state['download_clicked']:
                st.success("✅ You've nailed it! Your new pay ranges are now ready to be implemented.")
                # Reset the state after displaying the success message
                st.session_state['download_clicked'] = False


            
    st.write("")
    st.write("")

    # Display success message if the download button was clicked
    if st.session_state['download_clicked']:
                st.success("✅ You've nailed it! Your new pay ranges are now ready to be implemented.")
    st.write("")
    st.write("")

        # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    with col2:
            if st.button("← Previous", key="page6_previous_button"):
                st.session_state.page = 'page5'
                st.rerun()
    with col3:
            if st.button("Home →", key="page6_home_button"):
                st.session_state.page = 'home'
                st.rerun()

    st.markdown(
            '<span style="font-size: 0.8em; font-weight: lighter;"> Facing challenges with compensation or HR? Visit RewardsDNA.com to explore intuitive tools, request new features, or just drop us a message at hello@RewardsDNA.com!</span>',
            unsafe_allow_html=True)


st.write(st.session_state)
    


# Call the show function to render the Streamlit app
# show()

