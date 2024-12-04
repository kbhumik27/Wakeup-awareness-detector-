
# WakeUp (Awareness Detector)

![mermaid-diagram-2024-12-04-071138](https://github.com/user-attachments/assets/81d4b99d-5dab-48c4-9f00-b209d30c61b2)


WakeUp is a Python-based project designed to monitor and enhance user alertness through real-time facial analysis. This project leverages computer vision and machine learning techniques using **MediaPipe**, **OpenCV**, and **Google Text-to-Speech**. It detects eye blinks, yawns, and gaze direction to alert users to potential drowsiness or inattentiveness, making it ideal for drivers, students, or professionals requiring sustained attention.

## Features

- **Blink Detection:** Tracks the number of blinks using Eye Aspect Ratio (EAR).
- **Yawn Detection:** Measures lip distance to detect yawns and plays an audio alert when a yawn is detected.
- **Gaze Detection:** Identifies the user's gaze direction (center, left, or right).
- **Real-Time Feedback:** Displays visual feedback (blink count, gaze direction) and audio alerts for detected drowsiness signs.
- **Customizable Thresholds:** Adjustable parameters for EAR, yawn distance, and gaze sensitivity.

## Requirements

Ensure you have the following libraries installed:

- `mediapipe`
- `opencv-python`
- `numpy`
- `gtts`
- `playsound`

You can install the dependencies using the following command:

```bash
pip install mediapipe opencv-python numpy gtts playsound
```

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/wakeup-awareness-detector.git
    cd wakeup-awareness-detector
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the script:
    ```bash
    python wakeup.py
    ```

## Usage

1. Ensure your webcam is connected.
2. Launch the script to start the awareness detection.
3. Visual feedback and alerts will appear on the screen, such as:
   - **Blink Count**
   - **Gaze Direction** (e.g., *Looking Left*, *Looking Center*, or *Looking Right*)
   - **Yawn Alerts** displayed on-screen and played via audio.

Press `ESC` to exit the application.

## File Structure

```
wakeup-awareness-detector/
│
├── wakeup.py           # Main script for running the awareness detector
├── requirements.txt    # Dependencies for the project
└── README.md           # Project documentation
```

## Customization

- **Blink Detection Sensitivity:**
  Adjust `EYE_AR_THRESH` and `EYE_AR_CONSEC_FRAMES` in the code for tuning blink detection.

- **Yawn Detection Threshold:**
  Modify `YAWN_THRESH` for different sensitivity levels of yawn detection.

- **Gaze Direction Threshold:**
  Change `GAZE_THRESH` to alter the gaze direction sensitivity.

## Known Issues

- Background noise may cause inaccuracies in lip distance measurement.
- The program is optimized for frontal faces; side profiles may not yield accurate results.
- Audio playback issues on some systems. Ensure that `playsound` and audio drivers are correctly configured.

## Contribution

Contributions are welcome! If you encounter bugs or have feature suggestions, please submit an issue or a pull request.

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software with attribution.

---

### Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for its robust face detection and mesh modules.
- [OpenCV](https://opencv.org/) for real-time image processing.
- [gTTS](https://pypi.org/project/gTTS/) for text-to-speech alerts.

Stay alert, stay safe!
```
