import { useState } from 'react'
import axios from 'axios'
import React from "react";

function App() {
  const [file, setFile] = useState(null)
  const [downloadUrl, setDownloadUrl] = useState(null)

    const handleUpload = async () => {
    if (!file) {
        alert("Aucun fichier sélectionné.")
        return
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
        console.log("=== Début upload ===")
        console.log("Fichier sélectionné :", file)
        
        // Afficher le contenu du FormData
        for (let pair of formData.entries()) {
        console.log("FormData entry:", pair[0], pair[1])
        }

        const resUpload = await axios.post('http://5.250.176.7:5001/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        })

        console.log("Réponse upload :", resUpload.status, resUpload.data)

        const resDownload = await axios.get(`http://5.250.176.7:5001/download/${file.name}`)
        console.log("Réponse download :", resDownload.status, resDownload.data)

        setDownloadUrl(resDownload.data.url)
    } catch (error) {
        console.error("Erreur durant l'upload :", error)

        // Axios renvoie parfois une réponse serveur même en erreur
        if (error.response) {
        console.error("Code HTTP :", error.response.status)
        console.error("Données d’erreur :", error.response.data)
        }

        alert("Erreur : " + error.message)
    }
    }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-4 bg-gray-50">
      <h1 className="text-3xl font-bold">Uploader une image</h1>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button
        onClick={handleUpload}
        className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Upload
      </button>
      {downloadUrl && (
        <a href={downloadUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
          Voir l'image
        </a>
      )}
    </div>
  )
}

export default App
