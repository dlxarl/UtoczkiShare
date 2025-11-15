import { useState } from 'react';
import API from './api';

interface SharePhotoProps {
  photoId: number;
  token: string;
}

export default function SharePhoto({ photoId, token }: SharePhotoProps) {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);

  const handleShare = async () => {
    if (!email) {
      setMessage('Please enter an email');
      setIsError(true);
      return;
    }

    setMessage('');
    setIsError(false);

    try {
      console.log(`Sharing photo ${photoId} with ${email}`);
      await API.post(
        '/photos/share/',
        {
          photo: photoId,
          shared_to: email,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      console.log(`Successfully shared photo ${photoId} with ${email}`);
      setMessage('Photo successfully shared!');
      setIsError(false);
      setEmail('');
    } catch (err: any) {
      setIsError(true);
      const status = err?.response?.status;
      const data = err?.response?.data;
      console.error('Share error:', { status, data, message: err.message });
      
      if (status === 400) {
        if (data.shared_to) {
          setMessage(data.shared_to[0] || 'Validation error');
        } else if (data.photo) {
          setMessage(data.photo[0] || 'Photo not found');
        } else if (data.non_field_errors) {
          setMessage(data.non_field_errors[0] || 'Error');
        } else if (typeof data === 'string') {
          setMessage(data);
        } else if (data.detail) {
          setMessage(data.detail);
        } else {
          setMessage('Error sharing photo');
        }
      } else if (status === 404) {
        setMessage('Photo or user not found');
      } else {
        setMessage(`Error: ${status || 'unknown'}`);
      }
    }
  };

  return (
    <div className="share-container">
      <small>Share (Enter Email):</small>
      <div className="share-controls">
        <input
          type="email"
          placeholder="User Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <button onClick={handleShare}>Share</button>
      </div>
      {message && (
        <p className={`share-message ${isError ? 'error' : 'success'}`}>
          <small>{message}</small>
        </p>
      )}
    </div>
  );
}