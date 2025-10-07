import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Insurance Premium Predictor",
    page_icon="🛡️",
    layout="wide"
)

# --- Data for Selectboxes ---
# These should match the options and city lists in your FastAPI backend
OCCUPATION_OPTIONS = [
    'retired', 'freelancer', 'student', 'government_job',
    'business_owner', 'unemployed', 'private_job'
]

# Combine city lists from the backend for the selectbox
TIER_1_CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
TIER_2_CITIES = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]
# We add an "Other" option for cities not in the list (which will be classified as Tier 3)
ALL_CITIES = sorted(TIER_1_CITIES + TIER_2_CITIES) + ["Other"]


# --- UI Layout ---
st.title("🛡️ Insurance Premium Predictor")
st.markdown("Enter the user's details below to predict their insurance premium category.")

# Using columns for a cleaner layout
col1, col2 = st.columns(2)

with col1:
    st.header("👤 Personal Details")
    age = st.number_input("Age", min_value=1, max_value=119, value=30, step=1)
    weight = st.number_input("Weight (in kg)", min_value=1.0, value=70.0, step=0.5)
    height = st.number_input("Height (in meters)", min_value=0.1, max_value=2.49, value=1.75, step=0.01, format="%.2f")
    smoker = st.radio("Is the user a smoker?", ("Yes", "No"), index=1)

with col2:
    st.header("💼 Professional & Location Details")
    income_lpa = st.number_input("Annual Income (in LPA)", min_value=0.1, value=10.0, step=0.5)
    occupation = st.selectbox("Occupation", options=OCCUPATION_OPTIONS, index=6)
    # Using a searchable selectbox for the long list of cities
    city = st.selectbox("City", options=ALL_CITIES, index=ALL_CITIES.index("Mumbai"))


# --- Prediction Logic ---
if st.button("Predict Premium Category", use_container_width=True):
    # Prepare the data payload to send to the FastAPI endpoint
    # The structure must match the Pydantic model in `app.py`
    payload = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": True if smoker == "Yes" else False,
        "city": "Unknown" if city == "Other" else city, # Handle the 'Other' case
        "occupation": occupation
    }

    # URL of your running FastAPI application
    API_URL = "http://127.0.0.1:8000/predict"

    try:
        # Show a spinner while waiting for the API response
        with st.spinner('🧠 Analyzing data and making a prediction...'):
            response = requests.post(API_URL, data=json.dumps(payload))

        # Check if the request was successful
        if response.status_code == 200:
            prediction_data = response.json()
            predicted_category = prediction_data.get('predicted_category')
            st.success(f"**Predicted Premium Category: `{predicted_category}`**")
            st.balloons()
        else:
            # Show an error if the API returned a non-200 status code
            st.error(f"API Error: Status Code {response.status_code}")
            try:
                # Try to show the detailed error from the API if available
                st.json(response.json())
            except json.JSONDecodeError:
                # If the response is not JSON, show the raw text
                st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API. Please ensure the backend is running. Error: {e}")