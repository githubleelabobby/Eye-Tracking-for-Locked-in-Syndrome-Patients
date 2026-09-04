import cv2
import mediapipe as mp
import math
import requests


# ---------------- MEDIAPIPE SETUP ----------------

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="face_landmarker.task"
    ),
    running_mode=RunningMode.VIDEO,
    num_faces=1
)

landmarker = FaceLandmarker.create_from_options(options)


# ---------------- LANDMARKS ----------------

LEFT_IRIS = 468
RIGHT_IRIS = 473

# Horizontal eye corners
LEFT_EYE_1 = 33
LEFT_EYE_2 = 133

RIGHT_EYE_1 = 362
RIGHT_EYE_2 = 263

# Vertical eye boundaries
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145

RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374


# ---------------- CALIBRATION ----------------

calibration = {
    "WATER": [],
    "TOILET": [],
    "PAIN": [],
    "HELP": []
}


# SAVED CALIBRATION VALUES

calibrated_values = {
    "WATER": (0.56, 0.49),
    "PAIN": (0.53, 0.42),
    "TOILET": (0.48, 0.44),
    "HELP": (0.49, 0.28)
}


current_calibration = None


# ---------------- CAMERA ----------------

camera = cv2.VideoCapture(0)

timestamp = 0


while True:

    success, frame = camera.read()

    if not success:
        print("Could not read camera")
        break


    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp += 33

    result = landmarker.detect_for_video(
        mp_image,
        timestamp
    )


    if result.face_landmarks:

        landmarks = result.face_landmarks[0]


        # ---------------- HORIZONTAL X RATIO ----------------

        left_iris_x = landmarks[LEFT_IRIS].x

        left_x1 = landmarks[LEFT_EYE_1].x
        left_x2 = landmarks[LEFT_EYE_2].x

        left_min_x = min(left_x1, left_x2)
        left_max_x = max(left_x1, left_x2)

        left_x_ratio = (
            (left_iris_x - left_min_x)
            / (left_max_x - left_min_x)
        )


        right_iris_x = landmarks[RIGHT_IRIS].x

        right_x1 = landmarks[RIGHT_EYE_1].x
        right_x2 = landmarks[RIGHT_EYE_2].x

        right_min_x = min(right_x1, right_x2)
        right_max_x = max(right_x1, right_x2)

        right_x_ratio = (
            (right_iris_x - right_min_x)
            / (right_max_x - right_min_x)
        )


        gaze_x = (
            left_x_ratio + right_x_ratio
        ) / 2


        # ---------------- VERTICAL Y RATIO ----------------

        left_iris_y = landmarks[LEFT_IRIS].y

        left_top_y = landmarks[LEFT_EYE_TOP].y
        left_bottom_y = landmarks[LEFT_EYE_BOTTOM].y

        left_min_y = min(left_top_y, left_bottom_y)
        left_max_y = max(left_top_y, left_bottom_y)

        left_y_ratio = (
            (left_iris_y - left_min_y)
            / (left_max_y - left_min_y)
        )


        right_iris_y = landmarks[RIGHT_IRIS].y

        right_top_y = landmarks[RIGHT_EYE_TOP].y
        right_bottom_y = landmarks[RIGHT_EYE_BOTTOM].y

        right_min_y = min(right_top_y, right_bottom_y)
        right_max_y = max(right_top_y, right_bottom_y)

        right_y_ratio = (
            (right_iris_y - right_min_y)
            / (right_max_y - right_min_y)
        )


        gaze_y = (
            left_y_ratio + right_y_ratio
        ) / 2


        # ---------------- RECORD CALIBRATION ----------------

        if current_calibration is not None:

            calibration[current_calibration].append(
                (gaze_x, gaze_y)
            )

            if len(calibration[current_calibration]) >= 30:

                x_values = [
                    point[0]
                    for point in calibration[current_calibration]
                ]

                y_values = [
                    point[1]
                    for point in calibration[current_calibration]
                ]

                average_x = sum(x_values) / len(x_values)
                average_y = sum(y_values) / len(y_values)

                calibrated_values[current_calibration] = (
                    average_x,
                    average_y
                )

                print(
                    current_calibration,
                    "CALIBRATED:",
                    "(",
                    round(average_x, 3),
                    ",",
                    round(average_y, 3),
                    ")"
                )

                current_calibration = None


        # ---------------- DETECT CLOSEST OPTION ----------------

        distances = {}

        for option, value in calibrated_values.items():

            calibrated_x = value[0]
            calibrated_y = value[1]

            distance = math.sqrt(
                (gaze_x - calibrated_x) ** 2 +
                (gaze_y - calibrated_y) ** 2
            )

            distances[option] = distance


        detected_option = min(
            distances,
            key=distances.get
        )


        # ---------------- SEND TO FLASK SERVER ----------------

        try:
            requests.post(
                "http://127.0.0.1:5000/gaze",
                json={"option": detected_option},
                timeout=0.1
            )
        except:
            pass


        # ---------------- DISPLAY ----------------

        cv2.putText(
            frame,
            f"X: {gaze_x:.2f}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Y: {gaze_y:.2f}",
            (30, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "LOOKING AT: " + detected_option,
            (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        # Calibration instructions

        if current_calibration:

            text = (
                "CALIBRATING "
                + current_calibration
            )

        else:

            text = (
                "W=Water T=Toilet "
                "P=Pain H=Help"
            )


        cv2.putText(
            frame,
            text,
            (30, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )


        # ---------------- SHOW CALIBRATED VALUES ----------------

        y_position = 185

        for option, value in calibrated_values.items():

            text = (
                f"{option}: "
                f"({value[0]:.2f}, {value[1]:.2f})"
            )

            cv2.putText(
                frame,
                text,
                (30, y_position),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            y_position += 30


    # ---------------- SHOW CAMERA ----------------

    cv2.imshow(
        "4 Option Gaze Calibration",
        frame
    )


    # ---------------- KEYBOARD CONTROLS ----------------

    key = cv2.waitKey(1) & 0xFF


    if key == ord("w"):

        calibration["WATER"] = []
        current_calibration = "WATER"

        print("Look at WATER - recording...")


    elif key == ord("t"):

        calibration["TOILET"] = []
        current_calibration = "TOILET"

        print("Look at TOILET - recording...")


    elif key == ord("p"):

        calibration["PAIN"] = []
        current_calibration = "PAIN"

        print("Look at PAIN - recording...")


    elif key == ord("h"):

        calibration["HELP"] = []
        current_calibration = "HELP"

        print("Look at HELP - recording...")


    elif key == ord("q"):

        break


camera.release()
cv2.destroyAllWindows()
landmarker.close()
