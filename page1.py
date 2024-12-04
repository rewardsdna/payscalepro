import streamlit as st
import pandas as pd

import os

def init_page1_state():
    if "selected_approach" not in st.session_state:
        st.session_state.selected_approach = None
    if "page1_completed" not in st.session_state:
        st.session_state.page1_completed = False

def save_selection_to_csv(selected_option):
    # Ensure the data_csv directory exists
    os.makedirs('data_csv', exist_ok=True)
    
    # Create a DataFrame with the selection
    df = pd.DataFrame({
        'selected_approach': [selected_option]
    })
    
    # Save to CSV
    df.to_csv('data_csv/selected_option.csv', index=False)

def show():
    # Initialize page state
    init_page1_state()

    # Add custom CSS for buttons
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h2 style='color: #4A90E2;'>What's your approach?</h2>
        """, unsafe_allow_html=True)

    # Radio buttons for options
    options = {
        "Market rates of jobs to create pay ranges": "**You got a competitive edge!**", 
        "Pay data of existing employees to build pay ranges": "**Yes, Fairness matters!**", 
        "A combination strategy as it's well aligned with my organization": "**It's a win-win!**"
    }

    # Try to load previous selection from CSV
    try:
        if os.path.exists('data_csv/selected_option.csv'):
            previous_selection = pd.read_csv('data_csv/selected_option.csv')['selected_approach'].iloc[0]
            st.session_state.selected_approach = previous_selection
    except Exception as e:
        st.error(f"Error loading previous selection: {e}")

    # Display the radio button with default value from session state
    selected_option = st.radio(
        "**I will use:**",
        list(options.keys()),
        index=None if st.session_state.selected_approach is None 
              else list(options.keys()).index(st.session_state.selected_approach),
        key="approach_selector"
    )

    # Update session state and save to CSV when selection changes
    if selected_option:
        st.session_state.selected_approach = selected_option
        st.session_state.page1_completed = True
        save_selection_to_csv(selected_option)

    # Add an expander with detailed explanations
    with st.expander("More about approaches here"):
        st.write("""
        **Market Rates of Jobs**  
        Builds pay ranges based on competitive market rates for similar roles in the industry or region to stay competitive and attract talent.
        
        **Pay Data of Existing Employees**  
        Creates pay ranges by analyzing current employee compensation to ensure internal equity and fair pay within the organization.
        
        **Combination Strategy (Market-Informed)**  
        Combines external market data with internal pay data to create balanced pay ranges that are both competitive and internally fair.
        """)

    # Show message based on selection
    if selected_option:
        st.write(options[selected_option])

    # Navigation buttons with better layout
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col4:
        if st.button("← Previous", key="home_button"):
            st.session_state.page = 'home'
            st.rerun()
    
    with col5:
        # Next button is disabled until an option is selected
        if st.button("Next →", 
                    disabled=not st.session_state.page1_completed,
                    key="next_button"):
            # Ensure selection is saved before moving to next page
            if st.session_state.selected_approach:
                save_selection_to_csv(st.session_state.selected_approach)
            st.session_state.page = 'page2'
            st.rerun()

    # Add spacing at the bottom
    st.write("")
    

    # Debug information  
    # st.write("Debug Info:")
    # st.write(f"Selected Approach: {st.session_state.selected_approach}")
    # st.write(f"Page 1 Completed: {st.session_state.page1_completed}")
    # if os.path.exists('data_csv/selected_option.csv'):
    #     st.write("Saved selection:", pd.read_csv('data_csv/selected_option.csv')['selected_approach'].iloc[0])