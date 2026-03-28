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
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>🚦 Traffic AI System (LIVE DASHBOARD)</h1>

      {/* PAYMENT SECTION (UKITAKA UNAWEZA KUIONDOA BAADAE) */}
      <Payment />

      <hr />

      <h2>Live Traffic Data</h2>

      {data ? (
        <div>
          <p>🚗 Cars: {data.cars}</p>
          <p>🚌 Buses: {data.buses}</p>
          <p>🚚 Trucks: {data.trucks}</p>
          <p>🚶 People: {data.people}</p>
        </div>
      ) : (
        <p>Loading data from AI...</p>
      )}
    </div>
  );
}

export default App;