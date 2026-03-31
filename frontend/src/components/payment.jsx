import React, { useState } from "react";

const Payment = () => {
  const [method, setMethod] = useState("");

  const handlePayment = (type) => {
    setMethod(type);
    alert(`Selected payment method: ${type}`);
  };

  return (
    <div className="payment-container">
      <div className="payment-card">
        <h1>Payment Page</h1>
        <p>Select your preferred payment method below</p>

        <div className="buttons">
          <button onClick={() => handlePayment("Card")}>
            Pay with Card
          </button>

          <button onClick={() => handlePayment("Mobile Money")}>
            Pay with Mobile Money
          </button>

          <button onClick={() => handlePayment("Bank Transfer")}>
            Bank Transfer
          </button>
        </div>

        {method && (
          <div className="selected">
            Selected: <b>{method}</b>
          </div>
        )}
      </div>
    </div>
  );
};

export default Payment;