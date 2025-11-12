Dependencies are listed in requirements.txt

Cd into the project directory and create a python virtual environment
python -m venv venv

ensure you activate your virtual environment
source /venv/Scripts/activate (Git Bash Terminal)

Install dependencies

pip install -r requirements.txt

NOTE: BEFORE STARTING THE APPLICATION
Pass in the CSV files, it will throw an error and tell you which ones to put in the home directory

To Start the front-end of the application, enter the home directory of the project and simply type:  
streamlit run main.py
