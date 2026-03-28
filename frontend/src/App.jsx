import { useEffect, useState } from "react";
import Payment from "./components/Payment";

function App() {
  const [token, setToken] = useState(null);
  const [form, setForm] = useState({
    username: "",
    password: ""
  });
  const [message, setMessage] = useState("");

  // =========================
  // LOAD TOKEN
  // =========================
  useEffect(() => {
    const saved = localStorage.getItem("token");
    if (saved) setToken(saved);
  }, []);

  // =========================
  // HANDLE INPUT
  // =========================
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  // =========================
  // REGISTER
  // =========================
  const handleRegister = async () => {
    try {
      const res = await fetch("http://localhost:10000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
      });

      const data = await res.json();

      if (res.ok) {
        setMessage("✅ Account created, login sasa");
      } else {
        setMessage("❌ " + data.msg);
      }
    } catch {
      setMessage("❌ Server error");
    }
  };

  // =========================
  // LOGIN
  // =========================
  const handleLogin = async () => {
    try {
      const res = await fetch("http://localhost:10000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem("token", data.token);
        setToken(data.token);
        setMessage("✅ Login success");
      } else {
        setMessage("❌ " + data.msg);
      }
    } catch {
      setMessage("❌ Server error");
    }
  };

  // =========================
  // LOGOUT
  // =========================
  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  // =========================
  // UI
  // =========================
  if (!token) {
    return (
      <div className="p-6 max-w-md mx-auto mt-20 bg-white shadow rounded-xl">
        <h2 className="text-xl font-bold mb-4">🔐 Login / Register</h2>

        <input
          type="text"
          name="username"
          placeholder="Username"
          className="w-full p-2 border mb-3 rounded"
          onChange={handleChange}
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          className="w-full p-2 border mb-4 rounded"
          onChange={handleChange}
        />

        <div className="flex gap-2">
          <button
            onClick={handleLogin}
            className="flex-1 bg-blue-600 text-white p-2 rounded"
          >
            Login
          </button>

          <button
            onClick={handleRegister}
            className="flex-1 bg-gray-600 text-white p-2 rounded"
          >
            Register
          </button>
        </div>

        {message && (
          <p className="mt-4 text-center text-sm">{message}</p>
        )}
      </div>
    );
  }

  // =========================
  // AFTER LOGIN
  // =========================
  return (
    <div>
      <div className="p-4 flex justify-between items-center bg-black text-white">
        <h1>🚦 Traffic AI Dashboard</h1>
        <button onClick={handleLogout} className="bg-red-500 px-3 py-1 rounded">
          Logout
        </button>
      </div>

      {/* PAYMENT UI */}
      <Payment />
    </div>
  );
}

export default App;