import React, { useState, useEffect } from 'react';
import axios from 'axios';

function VideoStream() {
  const [streamData, setStreamData] = useState({
    blinks: 0,
    gaze: 'Center',
    yawn: false
  });
  const [isStreamActive, setIsStreamActive] = useState(true); // State to manage stream status

  useEffect(() => {
    if (!isStreamActive) return; // Skip fetching stream data if the stream is stopped

    // Fetch video stream data periodically
    const fetchStreamData = async () => {
      try {
        const dataResponse = await axios.get('http://localhost:5000/data');
        setStreamData(dataResponse.data);
      } catch (error) {
        console.error('Error fetching stream data:', error);
      }
    };

    // Fetch data every 2 seconds
    const interval = setInterval(fetchStreamData, 2000);

    // Cleanup interval on component unmount or when the stream is stopped
    return () => clearInterval(interval);
  }, [isStreamActive]);

  // Stop stream handler
  const stopStream = () => {
    setIsStreamActive(false); // Set stream status to inactive
  };

  return (
    <div>
      <h2>Video Stream</h2>
      {isStreamActive ? (
        <img 
          src="http://localhost:5000/video" 
          alt="Video Stream" 
          style={{ maxWidth: '100%' }}
        />
      ) : (
        <p>The video stream is stopped.</p>
      )}

      {/* Stop Stream Button */}
      <button 
        className="stop-button" 
        onClick={stopStream} 
        disabled={!isStreamActive} // Disable if the stream is already stopped
      >
        Stop Stream
      </button>
    </div>
  );
}

export default VideoStream;
