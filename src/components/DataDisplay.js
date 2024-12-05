import React, { useState, useEffect } from "react";
import axios from "axios";

const DataDisplay = () => {
  const [data, setData] = useState({ blinks: 0, gaze: "Center", yawn: false });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/data"); // Flask backend data endpoint
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data from server:", error);
      }
    };

    const intervalId = setInterval(fetchData, 1000); // Update every second
    return () => clearInterval(intervalId); // Cleanup interval on component unmount
  }, []);

  return (
    <div>
      <h2>Real-Time Data</h2>
      <p><strong>Blinks:</strong> {data.blinks}</p>
      <p><strong>Gaze Direction:</strong> {data.gaze}</p>
      <p><strong>Yawning:</strong> {data.yawn ? "Yes" : "No"}</p>
    </div>
  );
};

export default DataDisplay;
