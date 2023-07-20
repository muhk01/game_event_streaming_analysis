# Game Event Streaming Analysis

This project purpose is to analyze event occure in gaming instances, suppose in a gaming match between two teams, we could simulate match event, and analyzing them,
using **Google PubSub** to simulate realtime event, and **Google Dataflow** to deploy **Apache Beam** pipeline job to analyzing the data.

# Fundamental Streaming Data Pipeline

## Fixed Window
![alt text](https://raw.githubusercontent.com/muhk01/game_event_streaming_analysis/main/exercise/img/fixed_window.PNG)

A tumbling window is a specific type of fixed window. In a tumbling window, you could specify a fixed duration for each window, tumbling windows are non-overlapping. They do not slide or have any overlap between consecutive windows. When the duration of a tumbling window is reached, it "tumbles" to the next fixed time interval, starting a new window.

By applying this code below, we could set window to 20 Second
```
beam.WindowInto(window.FixedWindows(20))
```

The window.FixedWindows(20) creates fixed windows of 20 units of time. For example, if the first data element arrives at timestamp 0, it will be placed in the window [0, 20) (from 0 inclusive to 20 exclusive). If another data element arrives at timestamp 15, it will also be placed in the window [0, 20) since the window size is fixed at 20 units of time.

For example, suppose we have the following data with timestamps:
```
('A', 1) at timestamp 0
('B', 2) at timestamp 10
('C', 3) at timestamp 25
('D', 4) at timestamp 45
```
With beam.WindowInto(window.FixedWindows(20)), the data will be divided into the following windows:

```
('A', 1) at timestamp 0
('B', 2) at timestamp 10
('C', 3) at timestamp 25
('D', 4) at timestamp 45
```

In summary, to process fixed streaming data it is beneficial to include timestamps in the data at the publisher (producer) side before sending it to a message queue or streaming system. Including timestamps in the data at the publisher side provides valuable information about when events occurred, which is essential for correct event time processing and accurate analysis in downstream consumers (subscribers).

Here are some reasons why adding timestamps at the publisher side is advantageous:

Event Ordering: As you mentioned, adding timestamps at the publisher side ensures that the order of events is preserved. When data is sent with timestamps, the consuming side (subscriber) can process the data in the correct event time order. This is crucial for time-based windowing and accurate aggregation of data over time windows.

Event Time Processing: Many streaming data processing systems, including Apache Beam, perform event time processing, where events are ordered based on their timestamps, rather than the order in which they arrive. By providing timestamps at the publisher side, you enable event time processing in the consuming pipeline.

Late Data Handling: Timestamps help handle late-arriving data accurately. If an event arrives with a timestamp indicating it belongs to a previous window, the consuming pipeline can process it accordingly, even if the event arrives late. This is important for correct analysis, especially when data may be delayed in transit or when processing is subject to variability.

Time-Based Windowing: Timestamps are essential for creating time-based windows in streaming data processing. Time-based windows group data elements based on their event times, allowing you to perform time-based aggregations and computations.

Data Synchronization: In distributed systems, multiple producers may be sending data to a central message queue or streaming system. By including timestamps at the producer side, you can ensure that data from different sources is synchronized based on event times, which is especially important in scenarios where data from multiple sources needs to be combined for analysis.

## Sliding Window

![alt text](https://raw.githubusercontent.com/muhk01/game_event_streaming_analysis/main/exercise/img/sliding_window.PNG)

A sliding window is another type of windowing strategy used in stream processing. Unlike fixed windows or tumbling windows, sliding windows allow overlapping of data between consecutive windows. The window "slides" or moves forward by a specified duration instead of "tumbling" to the next interval.

In a sliding window, you specify both a window size and a "sliding" or "advancement" duration. The window size determines the size of each window, and the sliding duration determines the frequency at which the window moves forward.

## Trigger Counter
Trigger is a mechanism that determines when to emit partial results (intermediate results) during the processing of windowed data. Triggers are essential for controlling how data is accumulated within windows and when to produce results for downstream processing. Triggers play a crucial role in both batch and streaming processing, but they are especially significant in streaming data scenarios. When data is being processed within windows, a trigger decides when to emit the intermediate results based on the arrival of data elements and the passage of time. 
Setup Custom trigger Counter :
```
beam.WindowInto(window.GlobalWindows(), trigger=Repeatedly(AfterCount(10)), accumulation_mode=AccumulationMode.ACCUMULATING)
```

This sets up a custom trigger for the windowing operation. The trigger used here is Repeatedly, which repeatedly fires the trigger condition based on the specified sub-trigger. In this case, the sub-trigger is AfterCount(10), which fires after every 10 data elements have been processed within the global window.

Suppose we have the following data:

```
Data: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
```
When using the specified windowing transformation, the data elements will all be grouped into a single global window. The custom trigger Repeatedly(AfterCount(10)) will fire after every 10 elements have been processed within the window.

The processing of the data elements will look like this:

1. Process the first 10 data elements (['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']).
2. The trigger AfterCount(10) fires, and the intermediate result for the first 10 elements is emitted.
3. Process the next 4 data elements (['K', 'L', 'M', 'N']).
4. The trigger AfterCount(10) fires again, and the intermediate result for the next 4 elements is emitted.
The final output will contain two intermediate results, one for each group of 10 elements, accumulated over time.

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



