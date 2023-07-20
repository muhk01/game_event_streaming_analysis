![image](https://github.com/muhk01/game_event_streaming_analysis/assets/57218286/d8d99734-6b3d-4b54-8211-c1fb6508f792)# Exercise of Fundamental Streaming Data Pipeline

## Tumbling Window
![alt text](https://raw.githubusercontent.com/muhk01/game_event_streaming_analysis/main/exercise/img/fixed_window.PNG)

A tumbling window is a specific type of fixed window. In a tumbling window, you could specify a fixed duration for each window, tumbling windows are non-overlapping. They do not slide or have any overlap between consecutive windows. When the duration of a tumbling window is reached, it "tumbles" to the next fixed time interval, starting a new window.

## Sliding Window

![alt text](https://raw.githubusercontent.com/muhk01/game_event_streaming_analysis/main/exercise/img/sliding_window.PNG)

A sliding window is another type of windowing strategy used in stream processing. Unlike fixed windows or tumbling windows, sliding windows allow overlapping of data between consecutive windows. The window "slides" or moves forward by a specified duration instead of "tumbling" to the next interval.

In a sliding window, you specify both a window size and a "sliding" or "advancement" duration. The window size determines the size of each window, and the sliding duration determines the frequency at which the window moves forward.
