import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email import encoders
from email.mime.base import MIMEBase
import smtplib
import pyrebase
import os
from dotenv import load_dotenv
import pandas as pd
import re
from main import main
import page1, page2, page3, page4, page5, page6

load_dotenv()

firebaseConfig = {
  "apiKey": "AIzaSyAJn_j5mTC03Ov9OYN0EoBZF282ES7KSBY",
  "authDomain": "payscalepro.firebaseapp.com",
  "databaseURL": "https://payscalepro-default-rtdb.firebaseio.com",
  "projectId": "payscalepro",
  "storageBucket": "payscalepro.firebasestorage.app",
  "messagingSenderId": "147017519482",
  "appId": "1:147017519482:web:fa6fff08f3f056162986c3",
  "measurementId": "G-Y7W6VGQ2XV"
}



firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
database = firebase.database()

EXCEL_FILE = "client_data\client_details.xlsx"
os.makedirs("user_data", exist_ok=True)

OWNER_EMAIL = "praveenviswam@gmail.com"  # Replace with the app owner's email
SENDER_EMAIL = "rewardsdna@gmail.com"  # Replace with the sender's email
SENDER_PASSWORD = "fwbx swhr rokp vffc"  # Replace with the sender's app password

countries = [
    "Canada", "India", "Ireland", "Mexico", "Philippines", 
    "Poland", "South Africa", "UK", "USA", "Rest of the World"
]

def validate_password(password):
    """Helper function to validate password."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None

def save_to_excel(name, email, country):
    """Save user details to Excel and send the updated file to the app owner."""
    try:
        new_entry = pd.DataFrame([{"Name": name, "Email": email, "Country": country}])
        if os.path.exists(EXCEL_FILE):
            existing_data = pd.read_excel(EXCEL_FILE, engine="openpyxl")
            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        else:
            updated_data = new_entry
        updated_data.to_excel(EXCEL_FILE, index=False, engine="openpyxl")

        send_excel_to_owner(EXCEL_FILE)
    except Exception as e:
        st.write("")

def send_welcome_email(user_name, user_email):
    """Send a welcome email to the user."""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        subject = "Welcome aboard"
        body = f"""
        Dear {user_name},

        Thank you for signing up. You're now one step closer to fair pay. Get started by logging in at [application url].

        Facing challenges with compensation/HR optimization? Visit RewardsDNA.com to explore intuitive tools, request new features, or just drop us a message at hello@rewardDNA.com

        Best,
        Team - RewardsDNA
        Email: hello@rewardDNA.com
        """

        msg = MIMEMultipart()
        msg['From'] = formataddr(("RewardsDNA", SENDER_EMAIL))
        msg['To'] = user_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
    except Exception as e:
        st.error(f"Error sending email: {e}")

def send_reset_link(email):
    """Send a password reset email to the user."""
    try:
        auth.send_password_reset_email(email)
        st.success(f"A password reset link has been sent to {email}.")
    except Exception as e:
        st.error(f"Error sending reset link: {e}")

    



def send_excel_to_owner(file_path):
    """Send the updated Excel file to the app owner."""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        subject = "Updated User Details"
        body = "Attached is the updated Excel sheet containing user details."

        msg = MIMEMultipart()
        msg['From'] = formataddr(("RewardsDNA Notifications", SENDER_EMAIL))
        msg['To'] = OWNER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_path)}",
            )
            msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, OWNER_EMAIL, msg.as_string())
    except Exception as e:
        st.error(f"Error sending Excel file to app owner: {e}")

if "page" not in st.session_state:
    st.session_state.page = "Sign In"
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

def navigate_to(page):
    st.session_state.page = page

if not st.session_state.is_logged_in:
    st.title("PayScale Pro")

    if st.session_state.page == "Sign In":
        st.subheader("Sign In")
        email = st.text_input("Email address", key="signin_email")
        password = st.text_input("Password", type="password", key="signin_password")
        if st.button("Sign In"):
            if not email or not password:
                st.error("Email and password cannot be empty.")
            else:
                try:
                    auth.sign_in_with_email_and_password(email, password)
                    st.session_state.is_logged_in = True
                    st.success("Logged in successfully!")
                    st.session_state.page = "home"
                    st.rerun()
                except Exception as e:
                    st.error(f"Please Enter Valid Details if you are a new user please signup")
        st.button("Sign Up", on_click=lambda: navigate_to("Sign Up"))

        # Forgot Password button
        if st.button("Forgot Password"):
            st.session_state.page = "Forgot Password"
            st.rerun()

        


    elif st.session_state.page == "Sign Up":
        st.subheader("Sign Up")
        name = st.text_input("Name")
        email = st.text_input("Email address", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        selected_country = st.selectbox("Country", countries)
        if st.button("Sign Up"):
            if not name or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                validation_message = validate_password(password)
                if validation_message:
                    st.error(validation_message)
                else:
                    try:
                        auth.create_user_with_email_and_password(email, password)
                        save_to_excel(name, email, selected_country)
                        send_welcome_email(name, email)
                        st.success(f"Account created successfully for {name}!")
                        navigate_to("Sign In")
                    except Exception as e:
                        st.error(f"Sign up error: {e}")
        st.button("Go to Sign In", on_click=lambda: navigate_to("Sign In"))

    elif st.session_state.page == "Forgot Password":
        st.subheader("Forgot Password")
        email = st.text_input("Enter your email address", key="forgot_email")
        if st.button("Reset Password"):
            if email:
                send_reset_link(email)
                             
            else:
                
                st.error("Please enter your email address.")
        st.button("Go to Sign In", on_click=lambda: navigate_to("Sign In"))
else:
    if st.session_state.page == "home":
        main()
    elif st.session_state.page == 'page1':
        page1.show()
    elif st.session_state.page == 'page2':
        page2.show()
    elif st.session_state.page == 'page3':
        page3.show()
    elif st.session_state.page == 'page4':
        page4.show()
    elif st.session_state.page == 'page5':
        page5.show()
    elif st.session_state.page == 'page6':
        page6.show()

