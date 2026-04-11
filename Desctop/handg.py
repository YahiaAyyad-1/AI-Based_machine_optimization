import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 1. MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, model_complexity=0, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# 2. Matplotlib 3D Window Setup
plt.ion() # Turn on interactive mode
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
fig.canvas.manager.set_window_title('3D Hand Landmarks')

def main():
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # Process frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Clear 3D plot for new frame
        ax.cla()
        ax.set_xlim3d(-0.5, 0.5)
        ax.set_ylim3d(-0.5, 0.5)
        ax.set_zlim3d(-0.5, 0.5)
        ax.set_xlabel('X')
        ax.set_ylabel('Z') # Switching Y and Z for better 3D perspective
        ax.set_zlabel('Y')

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw 2D on Camera Window
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Extract 3D Coordinates
                xs = [lm.x for lm in hand_landmarks.landmark]
                ys = [lm.y for lm in hand_landmarks.landmark]
                zs = [lm.z for lm in hand_landmarks.landmark]

                # Center the hand around the wrist (landmark 0) for better 3D visualization
                base_x, base_y, base_z = xs[0], ys[0], zs[0]
                xs = [x - base_x for x in xs]
                ys = [y - base_y for y in ys]
                zs = [z - base_z for z in zs]

                # Plot landmarks in 3D
                ax.scatter(xs, zs, ys, c='r', marker='o') # Note: Y and Z swapped for visualization

                # Draw Connections in 3D
                for connection in mp_hands.HAND_CONNECTIONS:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    ax.plot([xs[start_idx], xs[end_idx]], 
                            [zs[start_idx], zs[end_idx]], 
                            [ys[start_idx], ys[end_idx]], color='blue')

        # Update both windows
        cv2.imshow("Jetson Camera", frame)
        plt.pause(0.001)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    plt.close()

if __name__ == "__main__":
    main()

