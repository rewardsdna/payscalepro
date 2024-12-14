import streamlit as st
import pandas as pd
import openpyxl
import os


def get_selected_approach():
    try:
        if os.path.exists('data_csv/selected_option.csv'):
            df = pd.read_csv('data_csv/selected_option.csv')
            return df['selected_approach'].iloc[0]
    except Exception as e:
        st.error(f"Error reading selection: {e}")
    return None

def validate_numeric_columns(df, numeric_columns):
    """Validate and convert numeric columns"""
    errors = []
    for col in numeric_columns:
        if col in df.columns:
            try:
                # Convert to numeric, forcing errors for non-numeric values
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Round to integers
                df[col] = df[col].round(0)
                # Check for NaN values after conversion
                nan_count = df[col].isna().sum()
                if nan_count > 0:
                    errors.append(f"{col}: {nan_count} invalid numeric values found")
            except Exception as e:
                errors.append(f"Error converting {col} to numeric: {str(e)}")
    return df, errors

def validate_data(df, required_columns):
    """Validate the uploaded data"""
    validation_errors = []
    
    # Check minimum records
    if len(df) < 10:
        validation_errors.append("Dataset must contain at least 10 records")
    
    # Define numeric columns
    numeric_columns = ['Grade']
    if 'Base Pay' in required_columns:
        numeric_columns.append('Base Pay')
    if 'Target Pay' in required_columns:
        numeric_columns.append('Target Pay')
    
    # Validate numeric columns
    df, numeric_errors = validate_numeric_columns(df, numeric_columns)
    validation_errors.extend(numeric_errors)
    
    return df, validation_errors

def show():
    # Add custom CSS for buttons
    st.markdown("""
            <style>
            .stButton > button {
                width: 100%;
                border-radius: 5px;
                height: 3em;
            }
                    
            .stButton > button:hover {
                background-color: #4A90E2;  /* Color when hovered */
                cursor: pointer;  /* Cursor changes to pointer on hover */
                color: white;  /* Text color changes to white on hover */
            }        
            </style>
            """, unsafe_allow_html=True)

    # Title
    st.markdown("<h2 style='color: #4A90E2;'>Load your data</h2>", unsafe_allow_html=True)

    # Retrieve the selected option from CSV
    selected_option = get_selected_approach()
    
    if selected_option is None:
        st.error("Please go back and select an approach first.")
        if st.button("← Go Back"):
            st.session_state.page = 'page1'
            st.rerun()
        return

    st.write(f"**Selected Approach:** {selected_option}")

    # Define expected columns
    expected_columns = {
        "Market rates of jobs to create pay ranges": ["Job", "Grade", "Target Pay"],
        "Pay data of existing employees to build pay ranges": ["Employee ID", "Grade", "Job", "Base Pay", "Gender"],
        "A combination strategy as it's well aligned with my organization": ["Employee ID", "Grade", "Job", "Base Pay", "Target Pay","Gender"],
    }

    # Verify the selected option exists in expected_columns
    if selected_option not in expected_columns:
        st.error("Invalid approach selected. Please go back and select again.")
        if st.button("← Go Back"):
            st.session_state.page = 'page1'
            st.rerun()
        return

    st.info(f"Mandatory fields: {', '.join(expected_columns[selected_option])}")
    col1, col2 = st.columns(2)
    # Sample template for the selected option
    sample_data = {col: [f"Sample {col}"] for col in expected_columns[selected_option]}
    with col1:
        sample_df = pd.DataFrame(sample_data)
        st.write("**Data format:**")
        st.dataframe(sample_df, hide_index=True)

        # Download template button
    template_df = pd.DataFrame(columns=expected_columns[selected_option])
    with col2:
            st.write("**Sample Template:**")
            st.download_button(
                label="📥 Template",
                data=template_df.to_csv(index=False).encode('utf-8'),
                file_name="template.csv",
                mime="text/csv"
            )

    # File uploader for Excel files
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "xls", "csv"])

    # Check if a file has been uploaded
    if uploaded_file is not None:
        try:
            # Process the uploaded file
            imported_data = pd.read_excel(uploaded_file)

            # Validate if all expected columns are present
            required_columns = expected_columns[selected_option]
            if set(required_columns).issubset(imported_data.columns):
                # Validate data
                imported_data, validation_errors = validate_data(imported_data, required_columns)

                if validation_errors:
                    st.error("Please fix the following issues and reload the data:")
                    for error in validation_errors:
                        st.error(error)
                    # Clear session state if there are errors
                    if 'imported_data' in st.session_state:
                        del st.session_state['imported_data']
                else:
                    st.success("👍Your data is validated and ready to dive in!")
                    st.write(f"Number of records uploaded: {len(imported_data)}")

                    # Display the data and summary in expanders
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander("Summary"):
                            grade_summary = imported_data['Grade'].value_counts().reset_index()
                            grade_summary.columns = ['Grade', 'No of Records']

                            if 'Job' in imported_data.columns:
                                job_counts = imported_data.groupby('Grade')['Job'].nunique().reset_index()
                                job_counts.columns = ['Grade', 'No of Jobs']
                                grade_summary = pd.merge(grade_summary, job_counts, on='Grade')

                            if 'Employee ID' in imported_data.columns:
                                employee_counts = imported_data.groupby('Grade')['Employee ID'].nunique().reset_index()
                                employee_counts.columns = ['Grade', 'No of Employees']
                                grade_summary = pd.merge(grade_summary, employee_counts, on='Grade')

                            st.dataframe(grade_summary, hide_index=True)

                    with col2:
                        with st.expander("Your Data"):
                            st.dataframe(imported_data, hide_index=True)

                    # Save the imported data only if validation passes
                    try:
                        os.makedirs('data_csv', exist_ok=True)
                        imported_data.to_csv('data_csv/user_loaded_data.csv', index=False)
                        st.session_state['imported_data'] = imported_data
                    except Exception as e:
                        st.error(f"Error saving data: {e}")
                        if 'imported_data' in st.session_state:
                            del st.session_state['imported_data']
            else:
                missing_columns = set(required_columns) - set(imported_data.columns)
                st.error(f"The uploaded file is missing the following columns: {', '.join(missing_columns)}")
        except Exception as e:
            st.error(f"Error processing file: {e}")
            if 'imported_data' in st.session_state:
                del st.session_state['imported_data']
    else:
        st.info("*Upload a file to proceed.*")


    st.write(" ")
    st.write(" ")
    # Navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col4:
        if st.button("← Previous",key="next_button_from_page_2_to_1"):
            st.session_state.page = 'page1'
            st.rerun()

    with col5:
        # Enable Next button only if data is uploaded and validated
        if st.button("Next →", 
                    disabled='imported_data' not in st.session_state, key="next_button_from_page_2_to_3"):
            st.session_state.page = 'page3'
            st.rerun()

# Add spacing at the bottom
    st.write("")


# # Debug information (comment out in production)
# st.write("Debug Info:")
# st.write(f"Selected Approach: {selected_option}")
# st.write(f"Required Columns: {expected_columns[selected_option]}")
# if 'imported_data' in st.session_state:
#     st.write("Data loaded: Yes")
#     st.write(f"Columns in loaded data: {list(st.session_state['imported_data'].columns)}")