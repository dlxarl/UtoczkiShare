![UtoczkiShare Banner](https://repository-images.githubusercontent.com/1096744931/07ce89fd-8728-49cc-b650-0dca64c90fca)

# UtoczkiShare - Photo Sharing Web Application

This project is a secure web application built as a qualifying task for the Hack4Defence 2025 hackathon.

It allows users to register, log in, upload, view, and share their photos with other users. The backend is built with Django & Django Rest Framework, and the frontend is a single-page application built with React and TypeScript.

## Core Features

  * **User Authentication**
    Secure JWT-based authentication is used. Users can register with a unique username and email, and a password that is validated for strength. Login is handled by the `TokenObtainPairView` from the Simple JWT library.

  * **Photo Upload**
    Authenticated users can upload image files via a `multipart/form-data` endpoint. The backend saves the file to the `media/uploads/` directory and links the `Photo` object to the currently logged-in user (`owner`).

  * **Secure Media Access**
    All media files are served through a protected API endpoint (`/api/media/`). This view checks if the requesting user is either the `owner` of the photo or if a `PhotoShare` object exists linking the photo to that user. If neither is true, a `403 Forbidden` error is returned.

  * **Photo Sharing**
    Users can share their own photos with other registered users by providing their email address. The backend validates that the email exists, belongs to a valid user, and is not the owner's own email. If valid, a `PhotoShare` entry is created to link the photo to the target user.

  * **Photo Management & Feed**
    The main gallery (`PhotoListCreateView`) displays a combined list of photos the user owns and photos shared with them. Users can delete their own photos via the `PhotoDetailView` (`DELETE /api/photos/<id>/`), which will also remove the file from the server.

    ![Login Page](https://i.postimg.cc/3rdLfngH/Screenshot-2025-11-15-at-23-35-29.png)
    ![Main Page](https://i.ibb.co/93Z4Q3Tb/Screenshot-2025-11-15-at-23-34-31.png)

## Security Implementation

The application was built with security as a priority, focusing on requirements from the qualifying task.

  * **IDOR Protection**: All endpoints for viewing, deleting, and sharing photos are scoped to the authenticated user. A user cannot access or manage another user's photos by guessing IDs.
  * **Secure Password Storage**: All user passwords are hashed using Django's default password hashing system.
  * **Input Validation**: Serializers on the backend validate all user input, such as ensuring unique usernames/emails, strong passwords, and that shared-to users exist.

## Tech Stack

  * **Backend**: Django, Django Rest Framework, Simple JWT.
  * **Database**: PostgreSQL.
  * **Frontend**: React, TypeScript, Vite, Axios.
  * **Testing**: Django APITestCase.

## Setup and Running Instructions

### Backend (Django)

1.  **Navigate to the backend directory:**
    ```bash
    cd photos_app
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    (Create a `requirements.txt` file with the following content, then run `pip install -r requirements.txt`)
    ```
    django
    djangorestframework
    djangorestframework-simplejwt
    django-cors-headers
    psycopg2-binary
    gunicorn
    Pillow
    ```
4.  **Configure Database:**
    Open `photos_app/photos_app/settings.py` and update the `DATABASES` section with your PostgreSQL credentials.
5.  **Run migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Run the server:**
    ```bash
    python manage.py runserver
    ```

### Frontend (React)

1.  **Navigate to the frontend directory:**
    ```bash
    cd photos_app/web
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Configure Environment:**
    Create a `.env` file in the `photos_app/web` directory. Add your backend API address:
    ```
    VITE_API_URL=http://127.0.0.1:8000/api
    ```
4.  **Run the development server:**
    ```bash
    npm run dev
    ```

## Automated Tests

To run the full suite of backend integration and security tests:

1.  Navigate to the `photos_app` directory.
2.  Ensure your virtual environment is activated.
3.  Run the test command:
    ```bash
    python manage.py test
    ```
