# 🧠 Zadanie kwalifikacyjne – Aplikacja webowa do zarządzania zdjęciami

## 🎯 Cel zadania
Celem jest stworzenie prostej, ale bezpiecznej aplikacji webowej, umożliwiającej użytkownikom rejestrację, logowanie, przesyłanie, przeglądanie i udostępnianie zdjęć innym użytkownikom.

---

## 📋 Zakres funkcjonalny
Aplikacja powinna umożliwiać:
1. **Rejestrację nowych użytkowników** (z walidacją danych, np. unikalny e-mail, bezpieczne hasło).  
2. **Logowanie użytkowników** (przy użyciu sesji lub tokenów JWT).  
3. **Dodawanie zdjęć** – użytkownik może przesyłać zdjęcia (np. JPG/PNG), które są zapisywane po stronie serwera.  
4. **Przeglądanie i pobieranie własnych zdjęć.**  
5. **Udostępnianie zdjęć** – użytkownik może udostępnić wybrane zdjęcie innemu zarejestrowanemu użytkownikowi (tylko do podglądu).  
6. **Bezpieczny dostęp do zasobów** – użytkownik nie może uzyskać dostępu do zdjęć, które do niego nie należą, chyba że zostały mu udostępnione.

---

## 🔐 Wymagania bezpieczeństwa
Aplikacja powinna uwzględniać zabezpieczenia przed typowymi zagrożeniami, w tym:
- **IDOR (Insecure Direct Object Reference)**
- **XSS (Cross-Site Scripting)**
- **Bezpieczne przechowywanie haseł (np. hashowanie, hash + salt itp.)**

---

## 🧪 Testy automatyczne
Należy przygotować zestaw **testów automatycznych**, które obejmują:
- testy jednostkowe dla logiki aplikacji,  
- testy integracyjne lub e2e dla głównych ścieżek użytkownika

---

## 🧾 Kryteria oceny
1. Poprawność i kompletność funkcjonalności  (20 pkt.)
2. Zabezpieczenia aplikacji  (10 pkt.)
3. Jakość i czytelność kodu  (10 pkt.)
4. Zakres i jakość testów automatycznych (5 pkt.)  
5. Intuicyjność interfejsu użytkownika (5 pkt.)

---

## 🇬🇧 English version

### 🎯 Goal
Build a small but secure web application that allows users to register, log in, upload, view, and share photos with other users.

### 📋 Functional Requirements
The application should support:
1. **User registration** with data validation (unique email, strong password).  
2. **User login** using sessions or JWT tokens.  
3. **Photo upload** – users can upload images stored on the server.  
4. **Viewing and downloading own photos.**  
5. **Photo sharing** – users can share selected photos with other registered users (view-only).  
6. **Secure resource access** – users cannot access photos they do not own unless shared with them.

### 🔐 Security Requirements
Include protection against:
- **IDOR**
- **XSS**
- **Secure password storage (hashing, hashing + salt etc.)**

### 🧪 Testing
Provide automated tests covering:
- application logic (unit tests),  
- main user flows (integration/e2e tests).

### 🧾 Evaluation Criteria
1. Functional completeness and correctness  (20 pts)
2. Security implementation  (10 pts)
3. Code quality and structure  (10 pts)
4. Automated test coverage  (5 pts)
5. UI usability  (5 pts)

---
