import { useState } from 'react';
import API from './api';

export default function UploadPhoto({ token, onUploadSuccess }: { token: string; onUploadSuccess?: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      setLoading(true);
      console.log(`Uploading file: ${file.name}`);
      const response = await API.post('/photos/', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      console.log('Upload response:', response.data);
      alert('Photo uploaded successfully');
      setFile(null);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err: any) {
      const status = err?.response?.status;
      const data = err?.response?.data;
      console.error('Upload error:', { status, data, message: err.message });
      if (status || data) {
        alert(`Upload error: ${status} - ${JSON.stringify(data)}`);
      } else {
        alert('Upload error');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Photo</h2>
      <input 
        type="file" 
        onChange={e => setFile(e.target.files?.[0] || null)} 
        disabled={loading}
        accept="image/*"
        title="Select a photo to upload"
      />
      {file && <p style={{ fontSize: '0.9em', color: '#aaa', margin: '0.5rem 0' }}>✓ {file.name}</p>}
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
}