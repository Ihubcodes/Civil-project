import pandas as pd
import numpy as np
import streamlit as st
import google.generativeai as genai
from PIL import Image
import math
import json
import re
import time
from io import BytesIO

# Configure Google Generative AI
genai.configure(api_key="AIzaSyBl0w-RMMsvo1hZRQxnEz7vU6Gy8pX8Pe8")  # Replace with your actual API key

# Initialize the Google Generative Model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Function to analyze the image and extract details
def analyze_image(image, model, max_attempts=3, sleep_time=2):
    prompt = """
    Analyze the given image and determine whether it contains a valid 2D house plan. If the image is a house plan, calculate and provide the total built-up area by summing up the areas of all individual rooms, hallways, and other enclosed spaces.

If the image does not contain a valid 2D house plan, return an error message indicating that the image is not suitable for construction analysis.

    Analyze the uploaded image to confirm whether it contains a valid 2D house plan. If confirmed, extract all possible details as specified below:

1. Total Built-up Area: 
   - If the image shows the total area or area, report it directly. 
   - Otherwise, calculate it by summing all visible room and space dimensions.

2. Room Details: For each room, identify:
   - Exact dimensions (Length x Width in both feet and inches if possible)
   - Total area (in square feet)
   - Room type (e.g., bedroom, kitchen, living room, bathroom)

3. Door and Opening Specifications:
   - Identify doors, including type (e.g., single or double or MD,TD,BD,...), dimensions (if shown), and exact placement within the plan.

4. Openings:
    - Record any marked openings (e.g., "OP" or "O"), noting their specific location or connection between spaces.

5. Window and Slab Locations: 
   - List each window and slab shown in the image, with dimensions and precise placement if labeled as w,w1,w2,...

6. Covered Areas:
   - Identify labeled covered areas such as patios, balconies, porches, porticos, or verandas, with their respective dimensions.

7. Floor Count: 
   - State the total number of floors depicted in the plan.

8. Unique or Special Features:
   - Record any notable elements such as staircases, built-in furniture, storage units, or unique architectural features (e.g., fireplaces, columns).

Output Format:

- Validation: [Valid/Invalid]
- Total Floors: [Number]

- Rooms:
    - Room Type: [Room type]
      - Dimensions: [Exact dimensions in feet and inches]
      - Area: [Total area in square feet]

- Doors:
    - Type: [Single/Double]
      - Location: [Precise location]

- Openings:
    - Type: [Opening type] Between [Room1] and [Room2]

-Windows and Slabs:

    - Total Count: [Number of windows/slabs]
    - Dimensions: Use specified dimensions or 30" x 48" as default; if window is labeled as a toilet window, omit dimensions.
    - Location: [List each room where the window or slab is located]

- Covered Features:
    - Porches: [Yes/No]
    - Patios: [Yes/No, with dimensions if shown]
    - Porticos: [Yes/No, with dimensions if shown]
    - Verandas: [Yes/No, with dimensions if shown]
    - Staircases: [Count and Location]

- Built-up Area: [Sum of all areas in square feet or directly from the image]

    """
    attempt = 0
    last_output = None

    while attempt < max_attempts:
        response = model.generate_content([image, prompt])

        if response and response.text:
            current_output = response.text.strip()

            if current_output == last_output:
                break

            last_output = current_output

        time.sleep(sleep_time)
        attempt += 1

    return last_output
    

# Function to extract average from a quantity range or return the single value
def extract_average(value):
    if isinstance(value, str) and '-' in value:
        try:
            nums = [int(x.strip()) for x in value.split('-')]
            return sum(nums) / len(nums)
        except ValueError:
            return None
    else:
        try:
            return int(value)
        except ValueError:
            return None

# Function to process substructure Excel files
def process_substructure(file_path, sheet_name="Sheet1", home_area =750):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    def process_quantities(cell_value, home_area):
        if pd.isna(cell_value):  # Check for NaN values
            return ""
        
        values = str(cell_value).split("\n")
        multiplied_values = []

        for val in values:
            val = val.strip()
            if val:  # Check if the string is not empty
                try:
                    multiplied_value = np.ceil(float(val) * home_area)
                    multiplied_values.append(int(multiplied_value))
                except ValueError:
                    multiplied_values.append(val)  # Keep original value if conversion fails

        return ", ".join(map(str, multiplied_values))

    df['Updated Quantities'] = df.iloc[:, 3].apply(lambda x: process_quantities(x, home_area))
    df['Materials'] = df['Materials'].str.replace('\n', ', ', regex=False)
    df['Units'] = df['Units'].str.replace('\n', ', ', regex=False)

    output_df = df[['Stage', 'Equipment', 'Materials', 'Updated Quantities', 'Units', 'Duration']]
    output_df = output_df.replace([np.nan, None], '')
    output_df.index = range(1, len(output_df) + 1)

    return output_df

def display_html_file(html_path):
    # Read the HTML content from the file
    with open(html_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    
    return html_content

# Function to process superstructure Excel files
def process_superstructure(file_path, sheet_name="Sheet1", home_area=750):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    def process_quantities(cell_value, home_area):
        if pd.isna(cell_value):  # Check for NaN values
            return ""

        values = str(cell_value).split("\n")
        multiplied_values = []

        for val in values:
            val = val.strip()
            try:
                multiplied_value = int(np.ceil(float(val) * home_area))
                multiplied_values.append(multiplied_value)
            except ValueError:
                multiplied_values.append(val) 

        return ", ".join(map(str, multiplied_values))

    df['Updated Quantities'] = df['Quantities'].apply(lambda x: process_quantities(x, home_area))
    df['Materials'] = df['Materials'].str.replace('\n', ', ', regex=False)
    df['Units'] = df['Units'].str.replace('\n', ', ', regex=False)

    output_df = df[['Stage', 'Equipment', 'Materials', 'Updated Quantities', 'Units', 'Duration']]
    output_df = output_df.replace([np.nan, None], '')
    output_df.index = range(1, len(output_df) + 1)

    return output_df

def extract_built_up_area(response):
    # Regular expression to find the built-up area
    match = re.search(r'Built-up Area:\s*([\d.]+)\s*sq ft', response)
    if match:
        return float(match.group(1))  # Convert to float
    return None  # Change "Not found" to None


# Function to load and display the second sheet (Total Material)
def load_total_material(file_path, sheet_name="Sheet2"):
    total_material_df = pd.read_excel(file_path, sheet_name=sheet_name)
    total_material_df = total_material_df.replace([np.nan, None], '')
    total_material_df.index = range(1, len(total_material_df) + 1)
    return total_material_df
st.set_page_config(page_title="BuildSmart", page_icon="🏚️")

st.title("BuildSmart")

# Image upload
uploaded_image = st.file_uploader("Upload a 2D House Plan Image", type=["png", "jpg", "jpeg","webp"])

# Analyze the image only once and store the result in session state
if uploaded_image is not None:
    # Display the uploaded image
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded House Plan", use_column_width=True)

    # Analyze the image
    with st.spinner('Analyzing the image...'):
        response = analyze_image(image, model)

    if response:
        # Safely parse the JSON response
        if response:
            try:
        # Extract built-up area from the response
                total_sqft = extract_built_up_area(response)

                if total_sqft is None:  # Check for None
                    st.warning("Please upload a proper 2D plan.")
                else:
                    st.session_state.total_sqft = total_sqft 
            except json.JSONDecodeError:
                    st.error("Failed to parse the analysis response. Please try again with a valid 2D house plan.")
    else:
        st.error("Failed to analyze the image. Please try again with a proper 2D plan.")
else:
    st.warning("Please upload a 2D house plan ")

SUPERSTRUCTURE_FILE_PATH = r"D:\civil\Superstar.xlsx"
SUBSTRUCTURE_FILE_PATH = r"D:\civil\Sub structure.xlsx"

# If the image was analyzed and the area is available
if 'total_sqft' in st.session_state and st.session_state.total_sqft is not None:
    home_area = st.session_state.total_sqft  # Use the area from session state

    # Ensure home_area is a float
    home_area = float(home_area)

    # Show the HTML document's content before displaying the dataframes
    html_file_path = r"D:\civil\word.html"
    html_content = display_html_file(html_file_path)

    # Analyze the image to check if it's a valid house plan
    response = analyze_image(image, model)
    if response != "Analysis failed.":
        # Display the response in a scrollable text box
        st.text_area("House Plan Analysis", response, height=400, max_chars=None)

    st.subheader("Comprehensive House Construction Material Estimation")

    # Use st.markdown to display the content with HTML and CSS for bullet points
    st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{html_content}</div>", unsafe_allow_html=True)

    # Process and display Substructure Data
    output_substructure = process_substructure(SUBSTRUCTURE_FILE_PATH, home_area=home_area)  # Pass actual home_area
    st.subheader("Substructure Data")
    st.dataframe(output_substructure)

    # Process and display Superstructure Data
    output_superstructure = process_superstructure(SUPERSTRUCTURE_FILE_PATH, home_area=home_area)
    st.subheader("Superstructure Data")
    st.dataframe(output_superstructure)

    # Load and display the second sheet (Total Material)
    total_material_df = load_total_material(SUPERSTRUCTURE_FILE_PATH)
    st.subheader("Total Material")
    st.dataframe(total_material_df)

    # Allow the user to download the modified Excel file
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        output_substructure.to_excel(writer, sheet_name="Substructure")
        output_superstructure.to_excel(writer, sheet_name="Superstructure")
        total_material_df.to_excel(writer, sheet_name="Total")

    output.seek(0)
    st.download_button(
        label="Download",
        data=output,
        file_name="processed_construction_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
