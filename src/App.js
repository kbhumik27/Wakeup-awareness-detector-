import React, { useState, useEffect, useRef } from "react";
import VideoStream from "./components/VideoStream";
import DataDisplay from "./components/DataDisplay";
import './App.css';  // Ensure this import is at the top of App.js

function App() {
  const [alarmStatus, setAlarmStatus] = useState(false);
  const audioRef = useRef(null); // Ref to keep track of the audio element
  const videoRef = useRef(null); // Ref to keep track of the video element

  // Function to handle the sound playing in the frontend
  const playSound = () => {
    if (audioRef.current) {
      audioRef.current.play()
        .catch((error) => {
          console.error("Error playing sound:", error);
          alert("Error playing sound. Please ensure your browser allows audio playback.");
        });
    }
  };

  // Function to stop the sound
  const stopSound = () => {
    if (audioRef.current) {
      audioRef.current.pause();  // Pause the audio
      audioRef.current.currentTime = 0;  // Reset the audio to the beginning
    }
  };

  // Function to stop the video
  const stopVideo = () => {
    if (videoRef.current) {
      videoRef.current.pause();  // Pause the video
      videoRef.current.currentTime = 0;  // Reset the video to the beginning
    }
  };

  useEffect(() => {
    const checkYawn = async () => {
      try {
        const response = await fetch("http://localhost:5000/yawn-detected", {
          method: "POST",
        });
        const data = await response.json();

        if (data.alarm) {
          setAlarmStatus(true);
          playSound();
        } else {
          setAlarmStatus(false);
          stopSound();  // Stop the sound if the alarm status is false
          stopVideo();  // Stop the video if the alarm status is false
        }
      } catch (error) {
        console.error("Error fetching yawn detection:", error);
      }
    };

    const interval = setInterval(checkYawn, 1000); // Check every second
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <div className="header">
        <h1>Welcome to Drowsiness Detection App</h1>
      </div>

      {/* Alert box for yawn detection */}
      {alarmStatus && (
        <div className="alert-box">
          <p>Yawn Detected! Alarm is playing...</p>
        </div>
      )}

      {/* Video Stream and Data Display sections */}
      <div className="content">
        <div className="video-stream">
          <VideoStream ref={videoRef} /> {/* Pass the videoRef to the VideoStream component */}
        </div>
      </div>

      {/* Audio element with a ref to control it */}
      <audio ref={audioRef} src="/yawn_alert.mp3" />
    </div>
  );
}

export default App;
