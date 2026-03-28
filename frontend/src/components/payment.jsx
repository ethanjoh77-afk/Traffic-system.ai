import { useState } from "react";

export default function Payment() {
  const [phone, setPhone] = useState("");
  const [amount, setAmount] = useState(1000);

  const handlePay = () => {
    alert("Payment request sent!");
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>💰 Payment</h2>

      <input
        placeholder="Phone"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />

      <br /><br />

      <input
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />

      <br /><br />

      <button onClick={handlePay}>Pay</button>
    </div>
  );
}