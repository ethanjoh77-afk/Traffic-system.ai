import { useEffect, useState } from "react";
import API_URL from "./config";
import Payment from "./components/Payment.jsx";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/stats`)
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.log("API ERROR:", err));
  }, []);

  return (
    <div style={{
      padding: "20px",
      fontFamily: "Arial",
      backgroundColor: "#0f172a",
      color: "white",
      minHeight: "100vh"
    }}>
      
      <h1>🚦 Smart Traffic AI System</h1>
      <p>LIVE DASHBOARD</p>

      <Payment />

      <hr />

      <h2>📊 Live Traffic Data</h2>

      {data ? (
        <div style={{
          background: "#1e293b",
          padding: "15px",
          borderRadius: "10px"
        }}>
          <p>🚗 Cars: {data.cars}</p>
          <p>🚌 Buses: {data.buses}</p>
          <p>🚚 Trucks: {data.trucks}</p>
          <p>🚶 People: {data.people}</p>
        </div>
      ) : (
        <p>Loading data...</p>
      )}

    </div>
  );
}

export default App;