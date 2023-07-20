import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import os
from apache_beam import window
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime, AccumulationMode, AfterCount, Repeatedly

# Replace 'my-service-account-path' with your service account path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ''

# Replace with your input subscription id
input_subscription = ''

input_topic = 'projects/pubsubdemo1-393106/topics/pubsubDemo'
# Replace with your output subscription id
output_topic = ''

options = PipelineOptions()
options.view_as(StandardOptions).streaming = True

p = beam.Pipeline(options=options)

def decode_incoming(data):
    data_str = data.decode('utf-8')
    return data_str

def parse_element(element):
    # Split the incoming element and return word and count as a tuple
    key, value = element
    return str(key), int(value)

def encode_byte_string(element):
   element = str(element)
   return element.encode('utf-8')

def custom_timestamp(elements):
  unix_timestamp = elements[7]
  return beam.window.TimestampedValue(elements, int(unix_timestamp))

def calculateProfit(elements):
  buy_rate = elements[5]
  sell_price = elements[6]
  products_count = int(elements[4])
  profit = (int(sell_price) - int(buy_rate)) * products_count
  elements.append(str(profit))
  return elements

def key_pair(element_list):
  # key-value pair of (team_id, 1)
  print(element_list[0], ' ',element_list[8])
  return element_list[0],int(element_list[8])

pubsub_data= (
                p 
                | beam.io.ReadFromPubSub(subscription= input_subscription)
                | 'Remove extra chars' >> beam.Map(lambda data: (data.rstrip().lstrip()))         
                | 'Decode' >> beam.Map(decode_incoming)
                | 'Split Row' >> beam.Map(lambda row : row.split(','))                            
                | 'Filter By Country' >> beam.Filter(lambda elements : (elements[1] == "Mumbai" or elements[1] == "Bangalore"))
                | 'Create Profit Column' >> beam.Map(calculateProfit)      
		| 'Apply custom timestamp' >> beam.Map(custom_timestamp) 
                | 'Form Key Value pair' >> beam.Map(key_pair) 
                | 'Window' >> beam.WindowInto(window.FixedWindows(20))  #Trigger Sum after 20 Seconds
                | 'Group players and their score' >> beam.CombinePerKey(sum)
                | beam.Map(print)
                | 'Encode to byte string' >> beam.Map(encode_byte_string)
	             )


result = p.run()
result.wait_until_finish()
