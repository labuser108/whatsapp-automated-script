import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load contacts from CSV file
def load_contacts(csv_file):
    contacts = pd.read_csv(csv_file, dtype={'phone_number': str})
    return contacts

# Function to send WhatsApp message and image using Selenium
def send_whatsapp_message(phone_no, message, image_path, driver):
    # Replace \n with %0A to preserve new lines
    message_with_newlines = message.replace("\n", "%0A")
    
    # Open WhatsApp Web with the phone number and message
    whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_no}&text={message_with_newlines}"
    driver.get(whatsapp_url)
    
    try:
        # Wait for WhatsApp Web to load
        time.sleep(15)  # Give WhatsApp Web time to load properly
        
        # Wait for the chat to load and the send button to be clickable
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-tab="11"][aria-label="Send"]'))
        )
        
        # Attach image if the image path exists
        if image_path and os.path.exists(image_path):
            print(f"Attaching image for {phone_no}")
            
            # Click on the "Attach" button (paperclip icon)
            attach_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[title="Attach"]'))
            )
            attach_button.click()
            time.sleep(2)  # Short pause to allow the menu to open
            
            # Find the input field for Photos & Videos
            photo_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"][accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
            )
            
            # Upload the image using send_keys
            photo_input.send_keys(image_path)
            time.sleep(5)  # Wait for the image to upload
            
            # Wait for the send button to become clickable again (for the image)
            send_image_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label="Send"] span[data-icon="send"]'))
            )
            send_image_button.click()
            print(f"Image sent to {phone_no}")
            time.sleep(5)  # Give time for the image to be sent
        else:
            # If no image, just send the message
            send_button = driver.find_element(By.CSS_SELECTOR, 'button[data-tab="11"][aria-label="Send"]')
            send_button.click()
            print(f"Message sent to {phone_no}")
        
        # Wait after sending the message to ensure it is sent properly
        time.sleep(10)
    
    except Exception as e:
        print(f"Failed to send message to {phone_no}: {str(e)}")

# Function to send messages to all contacts from the CSV file
def send_messages(csv_file, message_file, image_file, driver):
    contacts = load_contacts(csv_file)
    
    # Read the message template from the text file
    with open(message_file, 'r') as file:
        message_template = file.read()
    
    for index, row in contacts.iterrows():
        name = row['name']
        phone_no = row['phone_number']
        opt_in = row['opt_in']  # Optional column to manage opt-in

        # Customize the message with the contact's name
        personalized_message = message_template.replace("[Name]", name)
        
        # Send the message and image if opt-in is 1
        if opt_in == 1:
            print(f"Sending message to {name} at {phone_no}")
            send_whatsapp_message(phone_no, personalized_message, image_file, driver)
        else:
            print(f"{name} has opted out of messages.")

# Example usage
if __name__ == "__main__":
    # Automatically download the correct version of ChromeDriver
    service = Service(ChromeDriverManager().install())
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service)
    
    # Open WhatsApp Web and log in manually (you only need to log in once)
    driver.get("https://web.whatsapp.com")
    input("Press Enter after logging in to WhatsApp Web...")

    # Path to the CSV file, message file, and image file
    csv_file = 'path/to/contacts.csv'  # Path to your contacts.csv file
    message_file = 'path/to/whatsapp_message.txt'  # Path to your message.txt file
    image_file = 'path/to/LordNarshimhaDev.jpg'  # Path to the image file (optional)
    
    # Send the messages and images to all contacts
    send_messages(csv_file, message_file, image_file, driver)

    # Close the browser
    driver.quit()
