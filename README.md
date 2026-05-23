# 📚 Social Library

![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-Backend-3776AB?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite)
![Bootstrap](https://img.shields.io/badge/Bootstrap-Frontend-7952B3?style=for-the-badge&logo=bootstrap)
![TMDB](https://img.shields.io/badge/TMDB-Movie_API-01B4E4?style=for-the-badge)

**Social Library** is a Django-based social media platform for discovering, tracking, reviewing, and sharing movies and books.

It combines ideas from **Goodreads**, **Letterboxd**, and a social activity feed. Users can explore media, build personal libraries, create custom lists, follow others, and interact through likes, comments, and notifications.

---

## 📌 Overview

Social Library allows users to:

- Discover movies and books
- Track watched, read, and planned content
- Rate media from 1 to 10
- Create custom movie/book lists
- Follow other users
- Like and comment on activities
- Receive notifications for social interactions

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 5.2 |
| Database | SQLite3 |
| Frontend | Django Templates, HTML, CSS, JavaScript |
| UI Framework | Bootstrap |
| Movie API | TMDB API |
| Book API | Open Library API |
| Main JS File | `static/library/library.js` |

---

## 🧠 System Architecture

```mermaid
flowchart LR
    User[User] --> UI[Django Templates]
    UI --> Views[Django Views]
    Views --> DB[(SQLite Database)]
    Views --> TMDB[TMDB API]
    Views --> OpenLibrary[Open Library API]
    DB --> Feed[Activity Feed]
    DB --> Notifications[Notifications]
```

---

## ✨ Core Features

### 🔍 Media Exploration

Users can browse movies and books using external APIs.

| Feature | Description |
|---|---|
| Movie discovery | Powered by TMDB API |
| Book discovery | Powered by Open Library API |
| Layout | Responsive multi-column grid |
| Images | Optimized with `object-fit: cover` and hidden overflow |
| Carousel | Removed in favor of a cleaner grid system |

---

### 🧠 Search & Filter System

Users can dynamically filter content by:

| Filter | Description |
|---|---|
| Genre | Filter movies/books by category |
| Release Year | Shows content from the selected year and newer |
| Rating Range | Supports `2–5`, `5–7`, and `7+` |
| Book Rating Handling | Rating input is disabled when book rating data is unavailable |

---

### 🪟 Content Detail Popup

Clicking a movie or book opens a detailed popup with:

- Large cover image
- Summary description
- Year, genre, and metadata
- Duration or page count
- Watch/read status controls
- Rating system from 1 to 10
- Add-to-list option
- Comment popup

---

## 📂 User Library

The personal library page, **Kütüphanem**, uses a tabbed interface.

| Tab | Description |
|---|---|
| Watched | Movies the user has watched |
| To Watch | Movies the user wants to watch |
| Read | Books the user has read |
| To Read | Books the user wants to read |
| Custom Lists | User-created collections |

---

## 📝 Custom Lists

Users can:

- Create lists with an emoji and name
- Add movies and books to lists
- View lists inside content popups
- Keep movies and books organized separately

---

## 📰 Activity Feed

The platform includes an Instagram/Facebook-style activity feed.

| Feature | Description |
|---|---|
| User Avatar | Shows user profile image with fallback |
| Cover Image | Displays movie/book cover |
| Activity Text | Shows activity title and summary |
| Likes | Live like counter |
| Comments | Expandable comment panel |
| Logging | Centralized activity tracking |

---

## 🔔 Notifications

The homepage notification bell supports:

- New followers
- Likes
- Comments

### Fixed Notification Issues

| Problem | Solution |
|---|---|
| Bell displayed on wrong pages | Conditional homepage rendering |
| Duplicate avatar bug | Unified avatar fallback logic |
| Dropdown conflicts | Improved dropdown positioning |

---

## 🧩 Technical Challenge

### Problem

Keeping popup state consistent after user actions such as rating, commenting, or adding content to a list.

### Solution

User interactions are stored in the `Activity` and `ActivityDetail` models. Popup data is preloaded per user when opened, keeping the interface consistent after each action.

---

## 🧱 Project Structure

### Django Apps

| App | Purpose |
|---|---|
| `accounts` | Authentication, profiles, follows, activities, library |
| `explore` | Movie and book discovery |
| `core` | External API clients |

### Key Models

| Model | Purpose |
|---|---|
| `User` | Default Django user model |
| `Profile` | User profile information |
| `Activity` | Main activity feed records |
| `ActivityDetail` | Detailed activity metadata |
| `LibraryItem` | Watched/read/to-watch/to-read items |
| `CustomList` | User-created media lists |
| `Follow` | User follow relationships |
| `Notification` | Social notifications |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Bou-eng/social-library.git
cd social-library
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install django
pip install -r requirements.txt
```

If `requirements.txt` is missing, install the basic dependencies manually:

```bash
pip install django requests
```

---

### 4. Run Database Migrations

```bash
python manage.py migrate
```

---

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

> [!NOTE]  
> This step is optional but recommended for accessing the Django admin panel.

---

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open the project in your browser:

```text
http://127.0.0.1:8000/
```

---

## ⚙️ Development Notes

| Setting | Value |
|---|---|
| Language | Turkish |
| `LANGUAGE_CODE` | `tr` |
| Debug Mode | Enabled |
| Media Directory | `/media/` |
| Local Email Testing | `smtp4dev` |

---

## 🧪 Challenges & Solutions

| Problem | Solution |
|---|---|
| Duplicate avatars | Unified avatar rendering |
| API images not visible | CSS fix with `object-fit: cover` |
| Carousel drag issues | Replaced carousel with responsive grid |
| Broken notification bell | Conditional homepage rendering |
| Popup state inconsistency | Preloaded user-specific popup data |

---

## 🔮 Future Improvements

- Production-grade email service
- Performance optimizations
- ML-based recommendation system
- User-to-user messaging
- Real-time notifications

---

## 📚 References

- [Django Documentation](https://docs.djangoproject.com/)
- [TMDB API Documentation](https://developer.themoviedb.org/docs)
- [Open Library API Documentation](https://openlibrary.org/developers/api)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

---

## 📄 License

This project was developed for educational purposes.


And here are some screenshots of the project:
![WhatsApp Image 2026-01-29 at 7 05 44 PM (15)](https://github.com/user-attachments/assets/e5f8d858-4ffd-4d4c-84a9-ae81be008516)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (14)](https://github.com/user-attachments/assets/0dc0c83b-cf30-4087-99de-ca1c8d700612)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (13)](https://github.com/user-attachments/assets/57ee61cd-738f-442e-9412-b401a3815e7c)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (12)](https://github.com/user-attachments/assets/0e2602a1-dd3f-4c3d-9543-05b7b144f7d4)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (11)](https://github.com/user-attachments/assets/7ff74f92-b179-4ac3-9869-ea6968fbeb44)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (10)](https://github.com/user-attachments/assets/d4c2c39a-341b-40ce-b4e7-40204fd4e13f)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (9)](https://github.com/user-attachments/assets/a56a977f-2443-463e-9959-a327e4507059)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (8)](https://github.com/user-attachments/assets/100448dc-523b-4de0-9214-cc431c0d1ddc)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (7)](https://github.com/user-attachments/assets/9ed121ce-1760-4f9a-9510-2189c45a6a52)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (6)](https://github.com/user-attachments/assets/c9f8e302-85d1-45f1-bc0b-3a21da44a75f)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (5)](https://github.com/user-attachments/assets/c0fc3c3f-fe5e-4f9d-b488-e97bf0b4767f)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (4)](https://github.com/user-attachments/assets/b7a9e3b3-b009-4fe4-9cf4-25184928fb6e)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (3)](https://github.com/user-attachments/assets/a0268927-de66-4d5f-8b66-06c4637c1694)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (2)](https://github.com/user-attachments/assets/999f1326-d3b0-4b31-ac08-e60cd53d9e28)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (1)](https://github.com/user-attachments/assets/a9dae51d-6329-4239-aeca-06b3a226bda0)
![WhatsApp Image 2026-01-29 at 7 05 43 PM](https://github.com/user-attachments/assets/44254c2b-7492-45e8-bd8d-6947343733fb)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (7)](https://github.com/user-attachments/assets/46dd28b9-92c0-4002-b644-4515f7f5e6be)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (6)](https://github.com/user-attachments/assets/8092413a-0cec-4f79-9828-5ab44bfee3c2)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (5)](https://github.com/user-attachments/assets/e58e96f1-1fb1-4dab-9a1b-3b3d55c32622)
![WhatsApp Image 2026-01-29 at 7 05 44 PM](https://github.com/user-attachments/assets/89cee75d-d11a-4b62-bd65-8e350c8a6150)

