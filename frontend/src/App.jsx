import { useEffect, useState } from "react";
import Payment from "./components/Payment";
import API_URL from "./config";

function App() {
  const [stats, setStats] = useState(null);
  const [access, setAccess] = useState(null);

  useEffect(() => {
    // Access check
    fetch(`${API_URL}/access/user1`)
      .then(res => res.json())
      .then(data => setAccess(data))
      .catch(() => setAccess({ access: "blocked" }));

    // Traffic stats
    fetch(`${API_URL}/stats`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(() =>
        setStats({ cars: 0, buses: 0, trucks: 0, people: 0 })
      );
  }, []);

  return (
    <div style={{
      padding: "20px",
      fontFamily: "Arial",
      background: "#0f172a",
      minHeight: "100vh",
      color: "white"
    }}>
      <h1 style={{ textAlign: "center" }}>
        🚦 Traffic AI Dashboard
      </h1>

      {/* PAYMENT */}
      <Payment />

      {/* ACCESS STATUS */}
      <div style={{
        background: "#1e293b",
        padding: "15px",
        borderRadius: "10px",
        marginBottom: "20px"
      }}>
        <h3>🔐 System Status</h3>

        {access ? (
          access.access === "blocked" ? (
            <p style={{ color: "red" }}>
              ❌ Access Blocked (Pay Required)
            </p>
          ) : (
            <p style={{ color: "green" }}>
              ✅ Access Granted
            </p>
          )
        ) : (
          <p>Loading...</p>
        )}
      </div>

      {/* STATS */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(2, 1fr)",
        gap: "15px"
      }}>
        <div style={boxStyle}>
          <h3>🚗 Cars</h3>
          <p>{stats?.cars ?? 0}</p>
        </div>

        <div style={boxStyle}>
          <h3>🚌 Buses</h3>
          <p>{stats?.buses ?? 0}</p>
        </div>

        <div style={boxStyle}>
          <h3>🚚 Trucks</h3>
          <p>{stats?.trucks ?? 0}</p>
        </div>

        <div style={boxStyle}>
          <h3>🚶 People</h3>
          <p>{stats?.people ?? 0}</p>
        </div>
      </div>
    </div>
  );
}

const boxStyle = {
  background: "#334155",
  padding: "20px",
  borderRadius: "10px",
  textAlign: "center",
  fontSize: "18px"
};

export default App;