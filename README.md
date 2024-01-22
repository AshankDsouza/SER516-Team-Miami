# SER516-Team-Miami

# Taiga API Integration

This project is a Python script for interacting with the Taiga API to perform various task and calculating metrics.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3
- Required Python packages (install using `pip install -r requirements.txt`)
- Taiga account with API access
- Taiga project slug

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/ser516asu/SER516-Team-Miami.git
   cd SER516-Team-Miami
   ```
   
2. Install dependencies: 

    ```bash
   pip install -r requirements.txt
    ```


3. Create a .env file in the project root and add the following:

    ```bash
    TAIGA_URL=https://api.taiga.io/api/v1
    ```
   
4. Run the script:

    ```bash
    python3 app.py
    ```
