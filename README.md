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

## Trigger
Trigger is a mechanism that determines when to emit partial results (intermediate results) during the processing of windowed data. Triggers are essential for controlling how data is accumulated within windows and when to produce results for downstream processing. Triggers play a crucial role in both batch and streaming processing, but they are especially significant in streaming data scenarios. When data is being processed within windows, a trigger decides when to emit the intermediate results based on the arrival of data elements and the passage of time. 

There are several trigger example:

### Event Time Trigger:
An event time trigger fires based on the event timestamps of data elements. It allows you to control when to emit partial results based on the progress of event time in the data stream. In this example, we'll use AfterWatermark trigger, which fires when the watermark (representing the progress of event time) passes the end of the window.
```
import apache_beam as beam
from apache_beam.transforms.trigger import AfterWatermark

with beam.Pipeline() as p:
    data = p | beam.Create([
        ('A', 1, 10),  # Event 'A' with value 1, timestamp 10
        ('B', 2, 20),  # Event 'B' with value 2, timestamp 20
        ('A', 3, 15),  # Event 'A' with value 3, timestamp 15 (out-of-order)
    ])

    # Apply windowing based on event time (timestamps)
    windowed_data = data | beam.WindowInto(
        beam.window.FixedWindows(10),
        trigger=AfterWatermark(early=beam.transforms.trigger.AfterProcessingTime(2)),
        accumulation_mode=beam.transforms.trigger.AccumulationMode.DISCARDING
    )

    # Rest of the pipeline to process windowed_data
    # ...
```
In this example, we use a fixed window of size 10 units of time. The AfterWatermark trigger fires when the watermark passes the end of the window. We also use an early trigger AfterProcessingTime(2), which fires after 2 units of processing time, enabling early results. Accumulation mode is set to DISCARDING to discard early results.

### Processing Time Trigger:
A processing time trigger fires based on the processing time of data elements. It allows you to emit partial results periodically, based on processing time, regardless of event timestamps.
```
import apache_beam as beam
from apache_beam.transforms.trigger import AfterProcessingTime

with beam.Pipeline() as p:
    data = p | beam.Create([
        ('A', 1),
        ('B', 2),
        ('C', 3),
    ])

    # Apply windowing and trigger based on processing time
    windowed_data = data | beam.WindowInto(
        beam.window.FixedWindows(10),
        trigger=AfterProcessingTime(10),  # Trigger every 10 seconds
        accumulation_mode=beam.transforms.trigger.AccumulationMode.DISCARDING
    )

    # Rest of the pipeline to process windowed_data
    # ...
```
In this example, we use a fixed window of size 10 units of time. The AfterProcessingTime trigger fires every 10 seconds (based on processing time). Accumulation mode is set to DISCARDING to discard intermediate results.

### Data-Driven Trigger:
A data-driven trigger fires based on the data characteristics itself, rather than relying solely on time. For example, you can define a custom trigger based on the number of elements or certain conditions in the data.
```
import apache_beam as beam
from apache_beam.transforms.trigger import AfterCount

with beam.Pipeline() as p:
    data = p | beam.Create([1, 2, 3, 4, 5, 6, 7, 8, 9])

    # Apply windowing and data-driven trigger (AfterCount)
    windowed_data = data | beam.WindowInto(
        beam.window.FixedWindows(3),
        trigger=AfterCount(5),  # Trigger after 5 elements
        accumulation_mode=beam.transforms.trigger.AccumulationMode.DISCARDING
    )

    # Rest of the pipeline to process windowed_data
    # ...
```
In this example, we use a fixed window of size 3 elements. The AfterCount trigger fires when 5 elements have been processed within the window. Accumulation mode is set to DISCARDING to discard early results.

These are just examples to illustrate different triggers. The choice of trigger depends on your specific use case and desired behavior for processing data within windows. You can customize triggers, combine multiple triggers, and use complex logic to achieve the desired windowing behavior and control when to emit partial results.

### Accumulating Mode
![alt text](https://raw.githubusercontent.com/muhk01/game_event_streaming_analysis/main/exercise/img/trigger.PNG)

Accumulation Mode:
In the accumulating mode, when a trigger fires and produces a partial result, that result is accumulated and preserved until the window is closed. Subsequent trigger firings will accumulate additional partial results, and they all contribute to the final output for the window.
This mode is useful when you want to maintain intermediate results over time and combine them to produce the final output when the window is closed. Accumulating mode is commonly used for combining multiple partial results into a complete result, such as summing values or computing other aggregate statistics over a window.

Discarding Mode:
In the discarding mode, when a trigger fires and produces a partial result, that result is discarded and not preserved beyond the trigger firing. Each trigger firing produces a new partial result, but the previous results are not accumulated or maintained.
This mode is useful when you are only interested in the latest intermediate result and do not need to keep or combine previous partial results. Discarding mode is often used when the latest intermediate result is sufficient for further processing, and there is no need to accumulate or store historical partial results.
