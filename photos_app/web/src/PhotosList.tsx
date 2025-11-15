import { useEffect, useState } from 'react';
import API from './api';
import type { Photo } from './types';
import SharePhoto from './SharePhoto';
import type { AxiosResponse } from 'axios';

export default function PhotosList({ token }: { token: string }) {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    API.get('/photos/', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (res: AxiosResponse<Photo[]>) => {
        if (!mounted) return;
        const items: Photo[] = res.data;
        
        const validItems = items.filter(p => p.file && p.file.trim().length > 0);
        console.log(`Loaded ${items.length} photos, ${validItems.length} have files`);

        const apiBaseUrl = import.meta.env.VITE_API_URL;
        const withPreview = await Promise.all(
          validItems.map(async (p: Photo) => {
            try {
              console.log(`Fetching preview for file: ${p.file}`);
              const mediaUrl = `${apiBaseUrl}/media/${p.file}/`;
              console.log(`Absolute media URL: ${mediaUrl}`);
              const r = await fetch(mediaUrl, {
                headers: { Authorization: `Bearer ${token}` },
              });
              if (!r.ok) {
                throw new Error(`HTTP ${r.status}: ${r.statusText}`);
              }
              const blob = await r.blob();
              const url = URL.createObjectURL(blob);
              return { ...p, preview: url };
            } catch (e: any) {
              console.error(`Failed to load preview for ${p.file}:`, e.message);
              return p;
            }
          })
        );

        if (mounted) {
          setPhotos(withPreview);
        }
      });

    return () => {
      mounted = false;
      setPhotos((prevPhotos: Photo[]) => {
        prevPhotos.forEach(p => {
          if (p.preview) URL.revokeObjectURL(p.preview);
        });
        return [];
      });
    };
  }, [token]);

  const handleView = (blobUrl: string) => {
    window.open(blobUrl, '_blank');
  };

  const handleDownload = (blobUrl: string, originalName: string) => {
    const link = document.createElement('a');
    link.href = blobUrl;
    link.setAttribute('download', originalName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDelete = async (photoId: number, photoName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${photoName}"?`)) {
      return;
    }
    
    try {
      setLoading(true);
      console.log(`Deleting photo ID ${photoId}`);
      await API.delete(`/photos/${photoId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log(`Successfully deleted photo ID ${photoId}`);
      setPhotos(photos.filter(p => p.id !== photoId));
      alert('Photo successfully deleted');
    } catch (err: any) {
      const status = err?.response?.status;
      const data = err?.response?.data;
      console.error('Delete error:', { status, data, message: err.message });
      alert(`Error deleting photo: ${status} - ${JSON.stringify(data)}`);
    } finally {
      setLoading(false);
    }
  };

  const PhotoItem = (p: Photo) => (
    <li key={p.id} className="photo-item">
      {p.preview ? (
        <img src={p.preview} alt={p.original_name} />
      ) : (
        <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#242424' }}>
          <small>No preview</small>
        </div>
      )}
      
      <div className="photo-info">
        <strong>{p.original_name}</strong>
        
        {p.preview && (
          <div className="photo-actions">
            <button
              onClick={() => handleView(p.preview!)}
              className="action-button"
              disabled={loading}
            >
              View
            </button>
            <button
              onClick={() => handleDownload(p.preview!, p.original_name)}
              className="action-button download-button"
              disabled={loading}
            >
              Download
            </button>
            {p.isOwned && (
              <button
                onClick={() => handleDelete(p.id, p.original_name)}
                className="action-button delete-button"
                disabled={loading}
              >
                Delete
              </button>
            )}
          </div>
        )}
      </div>

      {p.isOwned && <SharePhoto photoId={p.id} token={token} />}
    </li>
  );

  return (
    <div className="photos-list-container">
      <h2>My Photos</h2>
      <OwnedPhotosSection 
        photos={photos.filter(p => p.isOwned)} 
        PhotoItem={PhotoItem}
      />
      
      <SharedPhotosSection
        photos={photos.filter(p => !p.isOwned)}
        PhotoItem={PhotoItem}
      />
    </div>
  );
}

function OwnedPhotosSection({ photos, PhotoItem }: { photos: Photo[], PhotoItem: any }) {
  if (photos.length === 0) {
    return <p style={{ color: '#888' }}>No photos uploaded</p>;
  }
  return (
    <ul className="photos-list">
      {photos.map((p: Photo) => PhotoItem(p))}
    </ul>
  );
}

function SharedPhotosSection({ photos, PhotoItem }: { photos: Photo[], PhotoItem: any }) {
  if (photos.length === 0) {
    return null;
  }
  return (
    <>
    
      <h2 style={{ marginTop: '2rem' }}>Shared with Me</h2>
      <ul className="photos-list">
        {photos.map((p: Photo) => PhotoItem(p))}
      </ul>
    </>
  );
}