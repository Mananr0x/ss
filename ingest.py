import os
import time
import json
from google.cloud import bigquery
import serial  # pip install pyserial

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "smart-sand-project-461f3ddf3a45.json"

# Initialize BigQuery client
client = bigquery.Client()
table_id = "smart-sand-project.sand_data.reading"

# Configure serial port (change as needed)
SERIAL_PORT = 'COM3'  # Example for Windows; change to your Arduino port
BAUD_RATE = 9600

def read_from_arduino():
    """Read data from Arduino via serial port."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for connection to establish
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"Received: {line}")
                yield line
    except serial.SerialException as e:
        print(f"Could not open serial port {SERIAL_PORT}: {e}")
        print("Falling back to generating dummy data for testing.")
        # Generate dummy data for testing if serial port is not available
        while True:
            # Simulate Arduino sending temperature and voltage
            import random
            temperature = round(random.uniform(25.0, 45.0), 1)
            voltage = round(random.uniform(1.5, 4.8), 2)
            timestamp = int(time.time())
            yield f"{temperature},{voltage},{timestamp}"
            time.sleep(5)  # Send a reading every 5 seconds
    except KeyboardInterrupt:
        print("\nStopping data ingestion.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def parse_data(line):
    """Parse a line of data from Arduino into a dictionary.
    Expected format: temperature,voltage,timestamp
    """
    try:
        parts = line.split(',')
        if len(parts) >= 3:
            temperature = float(parts[0])
            voltage = float(parts[1])
            timestamp = parts[2]
            return {
                "temperature": temperature,
                "voltage": voltage,
                "timestamp": timestamp
            }
        else:
            print(f"Warning: Unexpected data format: {line}")
            return None
    except ValueError as e:
        print(f"Error parsing data '{line}': {e}")
        return None

def insert_into_bigquery(rows):
    """Insert rows into BigQuery table."""
    errors = client.insert_rows_json(table_id, rows)
    if not errors:
        print(f"Inserted {len(rows)} rows into BigQuery.")
    else:
        print(f"Errors inserting rows: {errors}")

def main():
    print("Starting data ingestion from Arduino to BigQuery...")
    buffer = []
    buffer_size = 10  # Insert every 10 readings
    
    for line in read_from_arduino():
        parsed = parse_data(line)
        if parsed:
            buffer.append(parsed)
            if len(buffer) >= buffer_size:
                insert_into_bigquery(buffer)
                buffer = []  # Reset buffer
        time.sleep(0.1)  # Small delay to prevent overwhelming

if __name__ == "__main__":
    main()