# BuildSmart

BuildSmart is a Streamlit-based application that aids in analyzing 2D house plans and estimating construction materials for substructure and superstructure phases. It integrates advanced image analysis and data processing functionalities to streamline construction planning.

---

## Features

1. **2D House Plan Analysis**:
   - Users can upload a 2D house plan image.
   - The application analyzes the image to validate if it is a house plan.
   - Extracts details such as:
     - Total built-up area.
     - Room dimensions and areas.
     - Doors, openings, windows, and other structural details.

2. **Material Estimation**:
   - Uses the extracted built-up area to calculate the quantities of materials needed for substructure and superstructure stages.
   - Provides stage-wise details of equipment, materials, updated quantities, units, and durations.

3. **Data Presentation**:
   - Displays processed data in tabular format for:
     - Substructure data.
     - Superstructure data.
     - Total material requirements.
   - Includes an HTML preview of additional content.

4. **Downloadable Output**:
   - Generates an Excel file containing:
     - Substructure data.
     - Superstructure data.
     - Total material summary.

---

## Setup and Installation

### Prerequisites
- Python 3.7 or above
- Required Python libraries:
  - `pandas`
  - `numpy`
  - `streamlit`
  - `Pillow`
  - `xlsxwriter`

### Installation

1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd BuildSmart
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure your Google Generative AI API key is available. Replace the placeholder `AIzaSyBl0w-RMMsvo1hZRQxnEz7vU6Gy8pX8Pe8` in the code with your actual API key.

4. Place the necessary Excel files in the respective directories:
   - Substructure Excel file: `D:\civil\Sub structure.xlsx`
   - Superstructure Excel file: `D:\civil\Superstar.xlsx`
   - HTML content file: `D:\civil\word.html`

---

## Running the Application

1. Start the Streamlit app:
   ```bash
   streamlit run <script_name>.py
   ```

2. Open the local server URL (usually `http://localhost:8501`) in your web browser.

3. Use the application:
   - Upload a valid 2D house plan image.
   - View the analyzed plan details.
   - Access material estimation for substructure and superstructure.
   - Download the processed data as an Excel file.

---

## Code Description

### Image Analysis
The application integrates the Google Generative AI API to analyze uploaded images and extract house plan details such as:
- Built-up area.
- Room dimensions and types.
- Doors, windows, and openings.

### Material Processing
- Reads material data from Excel sheets for substructure and superstructure stages.
- Computes updated quantities based on the built-up area extracted from the image.

### Data Export
Generates a downloadable Excel file consolidating all the processed data for construction planning.

---

## File Structure
```plaintext
.
├── main.py                # Application script
├── requirements.txt       # List of required Python libraries
├── D:\civil\             # Directory containing external files
│   ├── Sub structure.xlsx
│   ├── Superstar.xlsx
│   └── word.html
```

---

## Notes
- Ensure valid 2D house plan images are uploaded for accurate analysis.
- Modify file paths in the code if your data files are stored in different locations.
- This application assumes well-structured Excel files with proper sheet names and data formats.

---

