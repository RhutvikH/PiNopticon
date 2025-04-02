from graphviz import Digraph

dot = Digraph(comment="Raspberry Pi Surveillance System Flowchart", format='png')

# Nodes with simple descriptions

# Start
dot.node("start", "Start: Program execution begins.")

# Initialization
dot.node("init", "Initialize Configuration and Variables")

# Open Video Stream
dot.node("open", "Open Video Stream")

# Stream decision
dot.node("stream_decision", "Stream Opened Successfully?")

# Error handling for stream
dot.node("error_stream", "Print error: Unable to open video stream!")
dot.node("exit", "Exit Program")

# Main loop
dot.node("main_loop", "Main Loop")

# Reading frame
dot.node("read_frame", "Read Frame from Video Stream")

# Decision for frame read
dot.node("frame_decision", "Frame Read Successfully?")

# Error for frame reading
dot.node("error_frame", "Print error: Unable to read frame\nBreak Loop")

# Get frame dimensions
dot.node("get_dimensions", "Get Frame Dimensions")

# YOLO detection
dot.node("yolo", "Run YOLOv8 Detection")

# Decision for person detection
dot.node("persons_decision", "Persons Detected?")

# Processing when person is detected
dot.node("select_bbox", "Select Largest Bounding Box")
dot.node("draw_bbox", "Draw Bounding Box and Label")
dot.node("calc_center", "Calculate Bounding Box Center")
dot.node("compute_angle", "Compute Target Servo Angle")

# Processing when no person is detected
dot.node("set_base", "Set Target Angle to Base")

# Smoothing target angle
dot.node("smooth", "Smooth Target Angle")

# Get current time
dot.node("get_time", "Get Current Time")

# Decision on update interval
dot.node("update_time_decision", "Time Since Last Update >= Interval?")

# Decision on angle change threshold
dot.node("angle_change_decision", "Angle Change Exceeds Threshold?")

# Sending servo command
dot.node("send_servo", "Send Servo Angle to Pi")

# Updating tracking variables
dot.node("update_tracking", "Update Tracking Variables")

# Display frame
dot.node("display", "Display Frame")

# Quit decision
dot.node("quit_decision", "Quit Key Pressed?")

# Break loop
dot.node("break_loop", "Break Loop")

# Cleanup
dot.node("cleanup", "Cleanup")

# End
dot.node("end", "End: Program terminates.")

# Edges for Initialization and stream check
dot.edge("start", "init")
dot.edge("init", "open")
dot.edge("open", "stream_decision")
dot.edge("stream_decision", "main_loop", label="Yes")
dot.edge("stream_decision", "error_stream", label="No")
dot.edge("error_stream", "exit")

# Edges for Main Loop frame processing
dot.edge("main_loop", "read_frame")
dot.edge("read_frame", "frame_decision")
dot.edge("frame_decision", "get_dimensions", label="Yes")
dot.edge("frame_decision", "error_frame", label="No")
dot.edge("error_frame", "cleanup")

# Continue after frame reading
dot.edge("get_dimensions", "yolo")
dot.edge("yolo", "persons_decision")
dot.edge("persons_decision", "select_bbox", label="Yes")
dot.edge("persons_decision", "set_base", label="No")
dot.edge("select_bbox", "draw_bbox")
dot.edge("draw_bbox", "calc_center")
dot.edge("calc_center", "compute_angle")
dot.edge("compute_angle", "smooth")
dot.edge("set_base", "smooth")
dot.edge("smooth", "get_time")
dot.edge("get_time", "update_time_decision")
dot.edge("update_time_decision", "angle_change_decision", label="Yes")
dot.edge("update_time_decision", "display", label="No")
dot.edge("angle_change_decision", "send_servo", label="Yes")
dot.edge("angle_change_decision", "display", label="No")
dot.edge("send_servo", "update_tracking")
dot.edge("update_tracking", "display")
dot.edge("display", "quit_decision")
dot.edge("quit_decision", "break_loop", label="Yes")
dot.edge("quit_decision", "read_frame", label="No")
dot.edge("break_loop", "cleanup")
dot.edge("cleanup", "end")

# Render the flowchart to a file and view it
dot.render('flowchart', view=True)
