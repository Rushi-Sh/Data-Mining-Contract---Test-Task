# Claw Legal Assignment

This project automates the process of fetching case details from the Indian eCourts portal using Selenium and displays the results in a Streamlit dashboard. Users can input a CNR number to retrieve and view case information.

## Features

- Automated CAPTCHA handling and form submission using Selenium.
- Extraction of detailed case information such as Filing Number, Filing Date, CNR Number, Case Stage, and Court Number and Judge.
- Streamlit dashboard for user-friendly interaction with organized tabs for different sections of case details.
- JSON output of case details with download functionality.

## Prerequisites

- Python 3.x
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/claw_legal_assignment.git
   cd claw_legal_assignment
   ```
2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3. Ensure ChromeDriver is installed and added to your PATH.
4. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
5. Open your web browser and go to  Open your web browser and go to URL_ADDRESS:8501 to access the Streamlit dashboard.
6. Enter the CNR number in the provided input field.
7. Click the "Submit" button to fetch and display case details.
8. The dashboard will display the case details in organized tabs.
9. You can download the JSON output by clicking the "Download JSON" button.
10. Enjoy!

## Project Structure
- main.py : Contains the core logic for interacting with the eCourts portal and extracting case details.
- app.py : Streamlit application for user interaction and displaying case details.
- .gitignore : Specifies files and directories to be ignored by Git.
- README.md : Project documentation.
## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.