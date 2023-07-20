# Exercise of Fundamental Streaming Data Pipeline

## Fixed Window
![alt text](https://raw.githubusercontent.com/muhk01/game_event_streaming_analysis/main/exercise/img/fixed_window.PNG)

A tumbling window is a specific type of fixed window. In a tumbling window, you could specify a fixed duration for each window, tumbling windows are non-overlapping. They do not slide or have any overlap between consecutive windows. When the duration of a tumbling window is reached, it "tumbles" to the next fixed time interval, starting a new window.

## Sliding Window

![alt text](https://raw.githubusercontent.com/muhk01/game_event_streaming_analysis/main/exercise/img/sliding_window.PNG)

A sliding window is another type of windowing strategy used in stream processing. Unlike fixed windows or tumbling windows, sliding windows allow overlapping of data between consecutive windows. The window "slides" or moves forward by a specified duration instead of "tumbling" to the next interval.

In a sliding window, you specify both a window size and a "sliding" or "advancement" duration. The window size determines the size of each window, and the sliding duration determines the frequency at which the window moves forward.

## Watermark 
Watermarks are used to determine how far the processing has progressed with respect to event time. The watermark indicates the maximum timestamp seen so far and acts as a progress marker for event time. When the watermark moves past a window's end time, the window is considered closed, and any remaining data is handled as late data.

Sample Code
```
import apache_beam as beam
from apache_beam.transforms.window import TimestampedValue
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime
from apache_beam.transforms.trigger import AccumulationMode
from apache_beam.transforms import window

# Sample data with explicit timestamps
data_with_timestamps = [
    TimestampedValue(('A', 1), 20),   # Element 'A' with timestamp 20
    TimestampedValue(('B', 2), 25),   # Element 'B' with timestamp 25
    TimestampedValue(('A', 3), 30),   # Element 'A' with timestamp 30
]

def format_output(element):
    return f"Window: {element[0]}, Values: {element[1]}"

with beam.Pipeline() as p:
    data = p | beam.Create(data_with_timestamps)

    # Apply fixed windows with allowed lateness of 10 seconds
    windowed_data = data | beam.WindowInto(window.FixedWindows(10), allowed_lateness=window.Duration(seconds=10))

    # Group elements by window and collect them as a list
    grouped_data = windowed_data | beam.GroupByKey()

    # Format the output for each window
    formatted_output = grouped_data | beam.Map(format_output)

    # Print the results
    formatted_output | beam.Map(print)
```

With allowing lateness to 10 Seconds then output should be
```
Window: 0, Values: [1, 2]
```

Here's what happens:

Element ('A', 1) arrives at timestamp 20. It belongs to the window [20, 30), which is the 10-second window starting at timestamp 20. It is processed as the first element in this window.

Element ('B', 2) arrives at timestamp 25. It also belongs to the window [20, 30). Since this window is still open, the element is added to the window and processed.

Element ('A', 3) arrives at timestamp 30. It belongs to the window [30, 40), which is the next 10-second window starting at timestamp 30. However, this window is considered late data because it arrives after the window's end time. By default, with allowed lateness set to 10 seconds, late data is dropped (LateDataDoFn.DISCARDING behavior). Therefore, this element ('A', 3) is discarded.

The output window is [20, 30), and the values are [1, 2], which includes elements ('A', 1) and ('B', 2) processed within the window. Element ('A', 3) is discarded because it is considered late data due to its arrival after the window's end time.


