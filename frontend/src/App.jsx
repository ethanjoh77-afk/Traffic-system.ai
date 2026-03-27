import { useState, useEffect } from "react";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [data, setData] = useState({});

  const login = async () => {
    const res = await fetch("http://127.0.0.1:5000/login", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({username,password})
    });
    const r = await res.json();
    if(r.token){
      localStorage.setItem("token", r.token);
      setToken(r.token);
    }
  };

  const register = async () => {
    await fetch("http://127.0.0.1:5000/register", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({username,password})
    });
    alert("registered");
  };

  const pay = async () => {
    const res = await fetch("http://127.0.0.1:5000/pay", {
      headers:{Authorization:token}
    });
    const r = await res.json();
    window.location.href = r.url;
  };

  useEffect(()=>{
    if(!token) return;

    const i = setInterval(()=>{
      fetch("http://127.0.0.1:5000/data", {
        headers:{Authorization:token}
      })
      .then(res=>{
        if(res.status===403){
          alert("💳 Pay first!");
          return {};
        }
        return res.json();
      })
      .then(setData);
    },1000);

    return ()=>clearInterval(i);
  },[token]);

  if(!token){
    return (
      <div>
        <input onChange={e=>setUsername(e.target.value)} placeholder="user"/>
        <input onChange={e=>setPassword(e.target.value)} type="password"/>
        <button onClick={login}>login</button>
        <button onClick={register}>register</button>
      </div>
    );
  }

  return (
    <div>
      <h1>SaaS Dashboard</h1>
      <button onClick={pay}>💳 Pay</button>

      <img src={`http://127.0.0.1:5000/video?token=${token}`} width="600"/>

      <h2>Cars {data.cars}</h2>
      <h2>Buses {data.buses}</h2>
      <h2>Trucks {data.trucks}</h2>
      <h2>People {data.people}</h2>
    </div>
  );
}