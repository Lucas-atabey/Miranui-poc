import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://5.250.176.204:5001';

export default function Auth({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = isRegister ? `${API_BASE}/register` : `${API_BASE}/login`;
      const res = await axios.post(url, { username, password });
      const token = res.data.access_token;
      onLogin(token);
    } catch (error) {
      alert('Erreur ' + (error.response?.data?.msg || error.message));
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-4 bg-gray-50">
      <h1 className="text-3xl font-bold">{isRegister ? 'Inscription' : 'Connexion'}</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 w-64">
        <input
          type="text"
          placeholder="Nom d'utilisateur"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="border p-2 rounded"
        />
        <input
          type="password"
          placeholder="Mot de passes"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="border p-2 rounded"
        />
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {isRegister ? "S'inscrire" : 'Se connecter'}
        </button>
      </form>
      <button
        onClick={() => setIsRegister(!isRegister)}
        className="text-blue-600 underline"
      >
        {isRegister ? 'Déjà un compte ? Connectez-vous' : "Pas de compte ? Inscrivez-vous"}
      </button>
    </div>
  );
}
