Dependencies are listed in requirements.txt

Cd into the project directory and create a python virtual environment
python -m venv venv

ensure you activate your virtual environment
source /venv/Scripts/activate (Git Bash Terminal)

Install dependencies (Note dependencies may take a little while to install)

pip install -r requirements.txt

NOTE: BEFORE STARTING THE APPLICATION
Pass in the CSV files, it will throw an error and tell you which ones to put in the home directory

To Start the front-end of the application, enter the home directory of the project and simply type:  
streamlit run main.py


Try some of these prompts!  
**Draw a pie chart for the percentage of airtime detected by pcl for high altitude slow speed orb flights**  
**show airtime detected by kairos for low altitude orb flights**  
fast, slow, medium speed  
high, low, medium altitude  
