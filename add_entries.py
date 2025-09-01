import requests
import random
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"  # Update this if your server runs on a different port
SUBMIT_URL = f"{BASE_URL}/submit"

# Lists for generating random entries
names = [
    "Priya", "Rahul", "Anita", "Raj", "Maya", "Vikram", "Neha", "Arjun",
    "Meera", "Arun", "Kavita", "Suresh", "Deepa", "Sanjay", "Anjali", "Amit",
    "Ritu", "Kunal", "Pooja", "Vijay", "Swati", "Aditya", "Nisha", "Rajesh"
]

surnames = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Verma", "Malhotra", "Shah",
    "Reddy", "Joshi", "Kapoor", "Mehta", "Chopra", "Desai", "Iyer", "Rao",
    "Das", "Nair", "Bose", "Menon", "Sinha", "Khanna", "Agarwal", "Bansal"
]

messages = [
    "Happy celebrations to everyone!",
    "Wishing you joy and prosperity",
    "Let's celebrate together!",
    "Sending festive wishes your way",
    "May this festival bring light to all",
    "Celebrating unity and happiness",
    "Spreading joy and cheer",
    "Best wishes for the festival",
    "Light up the world with kindness",
    "Together in celebration",
    "Sharing the spirit of festivity",
    "Wishing everyone peace and joy",
    "Happy festivities to all",
    "Celebrating with love and light",
    "May your day be filled with joy"
]

symbols = ["diya.png", "cracker.png", "rocket.png"]

def generate_entry():
    """Generate a random entry"""
    return {
        "name": f"{random.choice(names)} {random.choice(surnames)}",
        "message": random.choice(messages),
        "symbol": random.choice(symbols)
    }

def submit_entry(entry):
    """Submit an entry to the mosaic"""
    try:
        response = requests.post(SUBMIT_URL, data=entry)
        if response.ok:
            print(f"Successfully added entry for {entry['name']}")
            return True
        else:
            print(f"Failed to add entry for {entry['name']}: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error submitting entry: {e}")
        return False

def main():
    """Main function to add entries"""
    print("Starting to add entries to the mosaic...")
    
    # Number of entries to add
    num_entries = int(input("How many entries would you like to add? "))
    
    # Delay between submissions (in seconds)
    delay = float(input("Enter delay between submissions (in seconds, e.g., 0.5): "))
    
    successful = 0
    for i in range(num_entries):
        entry = generate_entry()
        if submit_entry(entry):
            successful += 1
        time.sleep(delay)  # Add delay between submissions
        
        # Print progress
        print(f"Progress: {i+1}/{num_entries} entries processed")
    
    print(f"\nCompleted! Successfully added {successful} entries out of {num_entries}")

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL)
        if response.ok:
            main()
        else:
            print("Error: Server is not responding correctly")
    except requests.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running at", BASE_URL)
