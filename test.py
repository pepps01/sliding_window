import time
import pytest
from sliding_window import SlidingWindowCounter  # Assuming the sliding window code is in this file
from dotenv import load_dotenv
import os

load_dotenv()

@pytest.fixture
def sliding_window():
    return SlidingWindowCounter(window_size_sec=5)

def test_add_event(sliding_window):
    sliding_window.add_event()
    sliding_window.add_event()
    assert sliding_window.get_event_count() == 2

def test_window_expiry(sliding_window):
    sliding_window.add_event()
    time.sleep(6)  # Wait for the window to expire
    assert sliding_window.get_event_count() == 0

def test_window_multiple_events(sliding_window):
    sliding_window.add_event()
    sliding_window.add_event()
    time.sleep(3)
    sliding_window.add_event()
    assert sliding_window.get_event_count() == 3  # Events are within the 5-second window

def test_kafka_env_vars():    
    kafka_topic = os.getenv('KAFKA_TOPIC')
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')    
    assert kafka_topic ==  os.getenv['KAFKA_TOPIC']
    assert bootstrap_servers == 'localhost:9092'
