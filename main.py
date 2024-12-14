import streamlit as st
st.set_page_config(page_icon="🌟",
    layout="wide")
import page1, page2 
from datetime import datetime
import os
from pathlib import Path



# Initialize session state variables
# def init_session_state():
#     if 'page' not in st.session_state:
#         st.session_state.page = 'home'
    # Add other session state variables here if needed
    # Example:
    # if 'data' not in st.session_state:
    #     st.session_state.data = None

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def get_greeting():
    current_time = datetime.now().hour
    if current_time < 12:
        return "🌄Good Morning!"
    elif 12 <= current_time < 16:
        return "🌈Good Afternoon!"
    else:
        return "🌆Good Evening!"

def main():
    # Initialize session state
    # init_session_state()

    # if st.session_state.page == 'home':
        st.title(get_greeting())

        st.markdown("""
            <h2 style='color: #4A90E2;'>Struggling with fair and competitive pay?</h2>
            """, unsafe_allow_html=True)
        
        
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
        
        

        st.write("The pay range builder empowers you to build data driven pay range, ensuring you attract top talent, retain your best, and manage compensation with confidence.")

        st.markdown("""
            - **Data-Driven**: No guess work and requires no effort for ensuring fit
            - **Multiple Approaches**: Choose an approach that best fits your organization
            - **Accurate Budgeting**: Identify outliers and align budgeting with your pay policy
            """)

        st.markdown("""
            Let's take another step towards fair pay! Create and fine tune your pay ranges now. All the best!
            """)    

        st.write("")
        st.write("")

        col1, col2, col3, col4, col5= st.columns([1, 1, 2, 1, 1])
        with col3:
            if st.button("I'm in →"):
                navigate_to('page1')

        with col2:
            if st.button("← Logout"):
                st.success("You have logged out successfully")
                st.session_state.is_logged_in = False
                navigate_to("Sign In")
                # st.rerun()
                
                
                
        # Check for dashboard data file
        with col4:
            data_file = Path("data_csv/pay_range_final.csv")
            if data_file.exists():
                if st.button("Dashboard → "):
                    navigate_to('page6')

        st.write("")
        st.write("")

        st.markdown(
    """
    
    <hr style="
        border: none; 
        border-top: 1px solid lightgray; 
        margin: 10px 0;"
    >
    <div style="
        text-align: center;
        font-size: 0.8em;
        font-weight: lighter;
        color: #4ca1ff;
    ">
        Job Profiler, Comp360, Edge, and Nudge are compensation informations for the rest of us. 
        Visit RewardsDNA.com today for your free access!
    </div>
    """,
    unsafe_allow_html=True
)
