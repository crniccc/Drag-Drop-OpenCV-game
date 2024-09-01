
---

# Connect Shapes

## Dependencies

This project requires the following Python libraries:

- **OpenCV (cv2):** For image and video processing.
- **cvzone:** For hand tracking and gesture recognition.
- **NumPy:** For numerical operations and handling arrays.
- **Random:** For generating random numbers and positions. (Note: This is part of the Python Standard Library and does not require separate installation.)
- **Warnings:** For managing warnings. (Note: This is part of the Python Standard Library and does not require separate installation.)

You can install the required libraries using pip:

```bash
pip install opencv-python cvzone numpy
```

## Connect Shapes - User Manual

### Game Overview

"Connect Shapes" is an exciting game that lasts 15 seconds. Your goal is to connect filled shapes with their corresponding empty shapes using hand gestures.

### How to Play

1. **Starting the Game:** Run the script `main.py` to start the game. The game interface will display shapes on the screen.
2. **Dragging and Dropping:**
   - For a better experience and accuracy, keep your hand about 50-60 cm away from the camera.
   - **Simulate Click:** To drag a shape, simulate a click by bringing the tips of your index finger and middle finger together.
   - **Moving Shapes:** Once the click is simulated, you can move the shape with your hand.
   - **Releasing Shapes:** To release a shape (stop moving), simply spread your index finger and middle finger apart.
   - **Restart and Exit:** Press the “R” key to restart the game or “Q” key to exit.
3. **Game Objective:** Connect filled shapes to empty shapes as quickly as possible. If the average accuracy is 90% or higher, you win!

### Controls

- **R:** Restarts the game, with shapes appearing in random positions.
- **Q:** Exits the game.

### Note

- The game lasts 15 seconds. Be quick and precise to achieve the best result!

---

