import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time
import random
import warnings

warnings.filterwarnings("ignore")

# Initialize camera and set resolution to 1280x720px
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize hand detector
detector = HandDetector(detectionCon=0.8)
colorFilled = (255, 0, 255)  # Color for "filled" shapes
colorOutline = (255, 0, 0)  # Color for "outline" shapes

# Class for dragging shapes
class DragShape:
    def __init__(self, shape, posCenter, size=[200, 200]):
        self.shape = shape  # Type of shape (rectangle, circle, triangle)
        self.posCenter = list(posCenter)  # Central position of the shape as a list with two elements
        self.size = size  # Dimensions of the shape (width, height)

    # Function to update the central position of the shape based on the cursor position
    def update(self, cursor):
        cx, cy = self.posCenter  # Coordinates of the shape's center
        w, h = self.size  # Width and height of the shape
        # Check if the cursor is within the shape
        if (cx - w // 2 < cursor[0] < cx + w // 2 and
                cy - h // 2 < cursor[1] < cy + h // 2):
            # If the index finger tip is within the shape, update the center position
            self.posCenter = list(cursor)

    # Draw the shape based on its current position and fill status
    def draw(self, img, fill=True):
        cx, cy = self.posCenter
        w, h = self.size
        if self.shape == 'rectangle':
            if fill:
                cv2.rectangle(img, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), colorFilled, cv2.FILLED)
            else:
                cv2.rectangle(img, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), colorOutline, 2)
        elif self.shape == 'circle':
            radius = min(w // 2, h // 2)
            if fill:
                cv2.circle(img, (cx, cy), radius, colorFilled, cv2.FILLED)
            else:
                cv2.circle(img, (cx, cy), radius, colorOutline, 2)
        elif self.shape == 'triangle':
            pts = np.array([(cx, cy - h // 2), (cx - w // 2, cy + h // 2), (cx + w // 2, cy + h // 2)], np.int32)
            pts = pts.reshape((-1, 1, 2))  # Convert the array of points from numpy format to a format suitable for OpenCV
            if fill:
                cv2.fillPoly(img, [pts], colorFilled)
            else:
                cv2.polylines(img, [pts], isClosed=True, color=colorOutline, thickness=2)

# Calculate the distance between a "filled" shape and an "outline" shape
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Create "filled" shapes
def create_shapes():
    # Possible positions
    positions = [
        [200, 150],
        [600, 150],
        [1000, 150]
    ]
    random.shuffle(positions)
    return [
        DragShape('rectangle', positions[0], size=[150, 150]),
        DragShape('circle', positions[1], size=[150, 150]),
        DragShape('triangle', positions[2], size=[150, 150])
    ]

# Create "outline" shapes
def create_outline_shapes():
    # Define possible positions
    positions = [
        [200, 450],
        [600, 450],
        [1000, 450]
    ]
    random.shuffle(positions)
    return [
        DragShape('rectangle', positions[0], size=[150, 150]),
        DragShape('circle', positions[1], size=[150, 150]),
        DragShape('triangle', positions[2], size=[150, 150])
    ]

# Reset game state
def reset_game_state():
    global moving_shape, result_displayed, timer_started, timer_finished, start_time
    # Reset the state
    moving_shape = None
    result_displayed = False
    timer_started = False
    timer_finished = False
    start_time = time.time()

# Create "filled" shapes
shapes = create_shapes()

# Create "outline" shapes
outline_shapes = create_outline_shapes()

# Timer settings and reset all items
total_duration = 15
reset_game_state()

# Function to restart the game
def restart_game():
    global shapes, outline_shapes
    shapes = create_shapes()
    outline_shapes = create_outline_shapes()
    reset_game_state()

while True:
    success, img = cap.read()
    if not success:
        break

    # Flip image horizontally for mirror effect
    img = cv2.flip(img, 1)

    # Update only if result is not displayed
    if not result_displayed:
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        remaining_time = total_duration - elapsed_time

        # Display timer on the screen (formatted to two decimal places)
        remaining_time_formatted = max(0, round(remaining_time, 2))
        cv2.putText(img, f'Time: {remaining_time_formatted}s',
                    (img.shape[1] - 300, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 255), 3, cv2.LINE_AA)

        # Detect hand
        hands, img = detector.findHands(img, True, False)
        if hands:
            for hand in hands:
                lmList = hand['lmList']  # List of 21 key points of the hand

                # Get coordinates of the index finger tip (point 8) and middle finger tip (point 12)
                x1, y1 = lmList[8][:2]
                x2, y2 = lmList[12][:2]

                # Calculate distance between the finger tips (detecting "click")
                length, _, _ = detector.findDistance((x1, y1), (x2, y2), img)

                # If "clicked"
                if length < 50:
                    cursor = lmList[8][:2]  # Cursor corresponds to the index finger tip
                    # Check if any shape is being moved
                    if moving_shape is None:
                        # Check if the click is within any of the 3 shapes
                        for shape in shapes:
                            cx, cy = shape.posCenter
                            w, h = shape.size
                            if (cx - w // 2 < cursor[0] < cx + w // 2 and
                                    cy - h // 2 < cursor[1] < cy + h // 2):
                                moving_shape = shape
                                break  # Only one object can be moved at a time
                    if moving_shape:
                        moving_shape.update(cursor)
                else:
                    moving_shape = None

        # Draw "filled" shapes
        for shape in shapes:
            shape.draw(img, fill=True)

        # Draw "outline" shapes
        for shape in outline_shapes:
            shape.draw(img, fill=False)

    # After timer expires
    if remaining_time <= 0:
        # Set flag to indicate that timer and result have been displayed (first frame after expiration)
        timer_finished = True
        result_displayed = True

        # Initialize message and color
        message = ""
        color = (255, 0, 0)
        # Calculate average match percentage and determine message if not already done
        match_percentages = []
        # Calculate distance between the centers of "filled" and "outline" shapes
        for filled_shape, empty_shape in zip(shapes, outline_shapes):
            dist = distance(filled_shape.posCenter, empty_shape.posCenter)
            if dist > 100:
                match_percentages.append(0)  # Percentage cannot be negative
            else:
                match_percentages.append(100 - dist)

        # Calculate average accuracy and determine message
        average_match = sum(match_percentages) / len(match_percentages)
        if average_match >= 90:
            message = 'Excellent!\nPress R to play again.'
            color = (255, 0, 0)
        else:
            message = 'You can do better!\nPress R to play again.'
            color = (0, 0, 255)

        if result_displayed:
            # Calculate position to display text
            text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
            text_x = (img.shape[1] - text_size[0]) // 2 + 100
            text_y = (img.shape[0] + text_size[1]) // 2

            # Calculate position to display average accuracy
            avg_text = f'Average: {average_match:.1f}%'
            avg_text_size = cv2.getTextSize(avg_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
            avg_text_x = (img.shape[1] - avg_text_size[0]) // 2
            avg_text_y = text_y - 50

            # Display result message in the center of the screen
            for i, line in enumerate(message.split('\n')):
                cv2.putText(img, line, (text_x, text_y + i * 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3, cv2.LINE_AA)

            # Display average accuracy above the result message
            cv2.putText(img, avg_text, (avg_text_x, avg_text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 2, cv2.LINE_AA)

    # Display image with messages and shapes in the window
    cv2.imshow('Connect the Shapes', img)
    # Handle key events
    key = cv2.waitKey(1)
    if key & 0xFF == ord('r'):
        restart_game()
    elif key & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
