import serial
import time
import os
from google.cloud import bigquery
from google.oauth2 import service_account

# Configuration
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
PROJECT_ID = 'smart-sand-project'
DATASET_ID = 'sand_data'
TABLE_ID = 'reading'
# Path to your Google Cloud service account key file
# Set this variable to the path of your JSON key file
SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-key.json'  # <-- UPDATE THIS

def initialize_bigquery_client():
    """Initialize and return a BigQuery client using service account credentials."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
    return client

def insert_reading(client, temperature, energy):
    """Insert a single sensor reading into BigQuery."""
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
    table = client.get_table(table_ref)
    
    # Prepare row data with server-generated timestamp
    row = [{
        "temperature": temperature,
        "energy": energy,
        "timestamp": time.time()  # Unix timestamp; BigQuery will convert to TIMESTAMP
    }]
    
    errors = client.insert_rows_json(table, row)
    if errors:
        print(f"BigQuery insert errors: {errors}")
    else:
        print(f"Inserted: Temp={temperature}°C, Energy={energy}")

def main():
    """Main function to read from Arduino and stream to BigQuery."""
    print("Starting IoT data bridge: Arduino -> BigQuery")
    print(f"Serial Port: {SERIAL_PORT} @ {BAUD_RATE} baud")
    print(f"Target: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    
    # Initialize BigQuery client
    try:
        client = initialize_bigquery_client()
        print("BigQuery client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize BigQuery client: {e}")
        return
    
    # Initialize serial connection
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow time for connection to establish
        print(f"Connected to Arduino on {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"Failed to connect to serial port {SERIAL_PORT}: {e}")
        return
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        # Parse "Temperature,Energy" format
                        parts = line.split(',')
                        if len(parts) == 2:
                            temperature = float(parts[0])
                            energy = float(parts[1])
                            insert_reading(client, temperature, energy)
                        else:
                            print(f"Warning: Unexpected format received: '{line}'")
                except ValueError as e:
                    print(f"Error parsing data '{line}': {e}")
                except UnicodeDecodeError as e:
                    print(f"Error decoding serial data: {e}")
            time.sleep(0.1)  # Reduce CPU usage
    except KeyboardInterrupt:
        print("\nStopping data bridge...")
    except Exception as e:
        print(f"Unexpected error in main loop: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()