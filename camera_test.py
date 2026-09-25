import cv2

# Open the laptop webcam
camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    if not success:
        print("Could not access the camera")
        break

    # Show webcam video
    cv2.imshow("Camera Test", frame)

    # Press Q to close
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()