import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = e => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post('/api/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Assume the API returns a statement ID as response.data.statement_id
      const statementId = response.data.statement_id || 1; // fallback for MVP demo
      navigate(`/dashboard/${statementId}`);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Bank Statement</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".pdf,.csv,.xlsx" />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
};

export default FileUpload;