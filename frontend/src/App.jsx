import { useEffect, useState } from "react";
import Payment from "./components/Payment.jsx";
import API_URL from "./config";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/stats`)
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.log(err));
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>🚦 Traffic AI System (LIVE)</h1>

      <Payment />

      <h2>Live Data:</h2>

      {data ? (
        <div>
          <p>Cars: {data.cars}</p>
          <p>Buses: {data.buses}</p>
          <p>Trucks: {data.trucks}</p>
          <p>People: {data.people}</p>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default App;