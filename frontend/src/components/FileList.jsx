import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://87.106.123.177:5001';

export default function FilesList({ token, refresh }) {
  const [files, setFiles] = useState([]);
  const [downloadUrls, setDownloadUrls] = useState({});

  useEffect(() => {
    axios
      .get(`${API_BASE}/files`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setFiles(res.data.files))
      .catch((err) => console.error(err));
  }, [token, refresh]);

  const handleDownload = (filename) => {
    axios
      .get(`${API_BASE}/download/${filename}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setDownloadUrls((prev) => ({ ...prev, [filename]: res.data.url }));
        window.open(res.data.url, '_blank');
      })
      .catch(() => alert('Erreur lors de la génération du lien'));
  };

  return (
    <div className="w-full max-w-lg mx-auto mt-6">
      <h2 className="text-xl font-semibold mb-4">Mes fichiers</h2>
      <ul>
        {files.map(({ filename }) => (
          <li
            key={filename}
            className="flex items-center justify-between mb-2"
          >
            <span>{filename}</span>
            <button
              onClick={() => handleDownload(filename)}
              className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Télécharger
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
