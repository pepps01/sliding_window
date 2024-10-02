import time
from kafka import KafkaConsumer
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

load_dotenv()

class SlidingWindowCounter:
    def __init__(self, window_size_sec, bucket_size_sec=1):
        self.window_size_sec = window_size_sec
        self.bucket_size_sec = bucket_size_sec
        self.num_buckets = window_size_sec // bucket_size_sec
        self.buckets = [0] * self.num_buckets
        self.timestamps = [0] * self.num_buckets
    
    def _get_bucket_index(self, current_time):
        return current_time % self.num_buckets
    
    def _reset_bucket(self, index, current_time):
        if self.timestamps[index] != current_time:
            self.buckets[index] = 0
            self.timestamps[index] = current_time
    
    def add_event(self):
        current_time = int(time.time())
        bucket_index = self._get_bucket_index(current_time)
        self._reset_bucket(bucket_index, current_time)
        self.buckets[bucket_index] += 1
    
    def get_event_count(self):
        current_time = int(time.time())
        total_events = 0
        for i in range(self.num_buckets):
            if current_time - self.timestamps[i] < self.window_size_sec:
                total_events += self.buckets[i]
        return total_events

    # Kafka event processing
    def consume_kafka_events(self, kafka_topic, bootstrap_servers):
        consumer = KafkaConsumer(kafka_topic, bootstrap_servers=bootstrap_servers)
        for message in consumer:
            print(f"Received message from Kafka: {message.value}")
            self.add_event()  # Process each event as it arrives

    # Kinesis event processing
    def consume_kinesis_events(self, stream_name, region_name):
        kinesis_client = boto3.client('kinesis', region_name=region_name)
        shard_id = kinesis_client.describe_stream(StreamName=stream_name)['StreamDescription']['Shards'][0]['ShardId']
        shard_iterator = kinesis_client.get_shard_iterator(StreamName=stream_name, ShardId=shard_id, ShardIteratorType='LATEST')['ShardIterator']
        
        while True:
            response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=100)
            records = response['Records']
            for record in records:
                print(f"Received record from Kinesis: {record['Data']}")
                self.add_event()  # Process each event
            shard_iterator = response['NextShardIterator']
            time.sleep(1)

# Example usage for Kafka and Kinesis
if name == "__main__":
    sliding_window = SlidingWindowCounter(window_size_sec=300)
    
    # Kafka setup
    kafka_topic = os.getenv['KAFKA_TOPIC']
    bootstrap_servers = ['localhost:9092']
    
    # Start Kafka consumer in a separate thread (or process)
    import threading
    kafka_thread = threading.Thread(target=sliding_window.consume_kafka_events, args=(kafka_topic, bootstrap_servers))
    kafka_thread.start()

    # Kinesis setup
    stream_name =  os.getenv['KINESIS_STREAM']
    region_name =  os.getenv['AWS_REGION']

    # Start Kinesis consumer in another thread (or process)
    kinesis_thread = threading.Thread(target=sliding_window.consume_kinesis_events, args=(stream_name, region_name))
    kinesis_thread.start()

    # Simulate event counting over time
    while True:
        print(f"Total events in last 5 minutes: {sliding_window.get_event_count()}")
        time.sleep(10)