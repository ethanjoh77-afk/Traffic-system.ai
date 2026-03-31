import { useState } from "react";
import API_URL from "../config";

export default function Payment() {
  const [msg, setMsg] = useState("");

  const pay = async () => {
    try {
      const res = await fetch(`${API_URL}/pay/mock`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "user1" })
      });

      const data = await res.json();
      setMsg(data.message);
    } catch (err) {
      setMsg("Payment failed");
    }
  };

  return (
    <div style={{
      padding: "15px",
      background: "#1e293b",
      borderRadius: "10px",
      marginBottom: "20px"
    }}>
      <h3>💳 Subscription</h3>

      <button
        onClick={pay}
        style={{
          padding: "10px",
          cursor: "pointer",
          borderRadius: "5px"
        }}
      >
        Unlock System
      </button>

      <p>{msg}</p>
    </div>
  );
}