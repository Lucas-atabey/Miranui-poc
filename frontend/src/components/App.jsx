import React, { useState } from 'react';
import axios from 'axios';
import FilesList from './FileList';

const API_BASE = 'http://5.250.176.204:5001';

export default function App({ token, onLogout }) {
  const [file, setFile] = useState(null);
  const [refreshFiles, setRefreshFiles] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert('Aucun fichier sélectionné.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);


    console.log("Fichier à uploader :", file);
    console.log("Token JWT :", token);
    try {
      await axios.post(`${API_BASE}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });
      alert('Upload réussi !');
      setFile(null);
      setRefreshFiles(prev => !prev);
    } catch (error) {
      if (error.response) {
        // Le serveur a répondu avec un status hors 2xx
        console.error("Erreur réponse serveur :", error.response.status, error.response.data);
        alert(`Erreur durant l'upload : ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      } else if (error.request) {
        // La requête a été envoyée mais pas de réponse reçue
        console.error("Pas de réponse reçue :", error.request);
        alert("Erreur durant l'upload : pas de réponse du serveur.");
      } else {
        // Autre erreur lors de la config de la requête
        console.error("Erreur setup requête :", error.message);
        alert("Erreur durant l'upload : " + error.message);
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start gap-6 p-4 bg-gray-50">
      <header className="w-full max-w-lg flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Uploader une image</h1>
        <button
          onClick={onLogout}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Déconnexion
        </button>
      </header>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />
      <button
        onClick={handleUpload}
        className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Upload
      </button>

      <FilesList token={token} refresh={refreshFiles} />
    </div>
  );
}
