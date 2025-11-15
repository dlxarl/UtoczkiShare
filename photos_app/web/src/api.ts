import axios from 'axios';

const apiUrl = import.meta.env.VITE_API_URL;

const API = axios.create({
  baseURL: apiUrl,
});

function getCookie(name: string): string | null {
  let cookieValue: string | null = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

API.interceptors.request.use((config) => {
  const csrftoken = getCookie('csrftoken');
  
  if (config.method && !['get', 'head', 'options'].includes(config.method.toLowerCase())) {
    if (csrftoken) {
      config.headers['X-CSRFToken'] = csrftoken;
    }
  }
  
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default API;