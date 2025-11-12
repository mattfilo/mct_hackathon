---
 
## 🛠️ Setup and Installation
 
### **1. Prerequisites**
 
All required Python packages are listed in `requirements.txt`.
 
### **2. Virtual Environment Setup**
 
It's best practice to use a virtual environment to isolate the project's dependencies.
 
* Change into your project directory:
    ```bash
    cd <project-directory>
    ```
 
* Create a virtual environment (named `venv`):
    ```bash
    python -m venv venv
    ```
 
* Activate the environment. **(Select the command appropriate for your system/terminal)**:
    * **Git Bash / Linux / macOS:**
        ```bash
        source venv/bin/activate
        ```
    * **Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate
        ```
    * **Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```
 
### **3. Install Dependencies**
 
Install the necessary libraries. This process may take a few moments.
 
```bash
pip install -r requirements.txt
streamlit run main.py
```

NOTE MAKE SURE YOU IMPORT THE PROPER CSV FILES INTO THE HOME DIRECTORY

Try some of these prompts
Draw a pie chart for the percentage of airtime detected by pcl for high altitude slow speed orb flights
 
Draw a pie chart for the percentage of airtime detected by pcl for low altitude slow speed orb flights
 
Draw a pie chart for the percentage of airtime detected by pcl for high altitude slow speed kairos flights
