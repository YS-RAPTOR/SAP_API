import tomlkit as toml 
import os.path as path
from tkinter import filedialog

def get_sap_path(showWindow = False) -> str:

    # Check if the config file exists
    if path.exists('config.toml') and not showWindow:

        # Load the config file
        with open ('config.toml', 'r') as f:
            config = toml.load(f)

        # read the path to the SAP.exe from the config file
        return config.get('SAP_PATH')
    else:

        # Open window to point to SAP.exe
        sap_path = filedialog.askopenfilename(initialdir="/", title="Select the Super Auto Pets executable", filetypes=(("Super Auto Pets.exe", "*.exe"), ("all files", "*.*")))

        # Save the path to the config file
        data = {'SAP_PATH': sap_path}
        with open('config.toml', 'w') as f:
            toml.dump(data, f)
        
        # Return the path
        return sap_path

def init() -> str:
    sap_path = get_sap_path()

    # Check if the path is valid
    while sap_path == None or not path.exists(sap_path):

        # If the path is invalid, ask for a new path
        print('SAP path is invalid')
        sap_path = get_sap_path(True)
    
    return sap_path