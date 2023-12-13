import sys
import os
import re
import json

def generate_config(extension, full_name, dhcp_hostname, agent_name):
    # Configuration template with placeholders for user-specific data
    config_template = f"""#!version:1.0.0.1

account.1.auth_name = {extension}
account.1.display_name = {full_name}
account.1.enable = 1
account.1.label = {extension} {agent_name}
account.1.sip_server.1.address = 154.117.190.42
account.1.user_name = {extension}
account.1.password = lotto@123
security.user_password = admin:lotto@123
features.direct_ip_call_enable = 0
features.missed_call_popup.enable = 0
features.power_saving.enable = 0
local_time.dhcp_time = 1
local_time.time_zone = +2
phone_setting.missed_call_power_led_flash.enable = 0
phone_setting.ring_type = Resource:Ring2.wav
sip.trust_ctrl = 1
###  Static Configuration  ###
static.network.dhcp_host_name = {dhcp_hostname}
"""
    return config_template

def save_config_file(content, mac_address):
    # Ensure the Configs directory exists
    folder_path = '/volume1/web/config'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Save the file with the MAC address as the filename
    file_path = os.path.join(folder_path, f"{mac_address.lower()}.cfg")
    with open(file_path, 'w') as file:
        file.write(content)

def validate_input(ext_number, full_name, dhcp_hostname, agent_name, mac_address):
    # Validation for all input fields
    if not all([ext_number, full_name, dhcp_hostname, agent_name, mac_address]):
        print("Error: All fields are required.")
        return False

    if not ext_number.isdigit():
        print("Error: Extension number must be numeric.")
        return False

    if not re.match("^[a-zA-Z ]+$", full_name):
        print("Error: Full name should contain only letters and spaces.")
        return False

    if not re.match("^[0-9A-Fa-f]{12}$", mac_address):
        print("Error: MAC address must be 12 hexadecimal characters.")
        return False

    return True

def process_json(json_file_path):
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            for record in data:
                if validate_input(record['Extension'], record['FullName'], record['DHCPHostname'], record['AgentName'], record['MACAddress']):
                    config_content = generate_config(record['Extension'], record['FullName'], record['DHCPHostname'], record['AgentName'])
                    save_config_file(config_content, record['MACAddress'])
                    print(f"Configuration file for {record['MACAddress']} has been created successfully.")
                else:
                    print(f"Invalid data in record: {record}")
    except Exception as e:
        print(f"Error processing JSON file: {e}")
                

def process_individual_config(args):
    # Process individual configuration
    ext_number, full_name, dhcp_hostname, agent_name, mac_address = args
    if validate_input(ext_number, full_name, dhcp_hostname, agent_name, mac_address):
        config_content = generate_config(ext_number, full_name, dhcp_hostname, agent_name)
        save_config_file(config_content, mac_address)
        print(f"Configuration file for {mac_address} has been created successfully.")

def main(args):
    # Check for individual configuration
    if len(args) == 6:
        process_individual_config(args[1:])
    # Check for JSON file processing
    elif len(args) == 2:
        process_json(args[1])
    else:
        print("Usage: python Yealink.py <ext_number> <full_name> <dhcp_hostname> <agent_name> <mac_address>")
        print("Or: python Yealink.py <path_to_json_file>")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)