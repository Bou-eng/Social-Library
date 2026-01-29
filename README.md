📚 Social Library

Social Library is a Django-based social media platform that combines movie & book discovery with personal libraries, reviews, and social interaction.
Think of it as a hybrid between Goodreads, Letterboxd, and a social activity feed.

Users can explore movies and books, track what they’ve watched or read, rate content, create custom lists, follow other users, and interact through likes, comments, and notifications.

🚀 Features
🔍 Media Exploration

Browse movies and books via TMDB and Open Library APIs

Responsive multi-column grid layout (carousel removed)

Poster images optimized using object-fit: cover and overflow: hidden

🧠 Search & Filter System

Dynamic filtering by:

Genre

Release year (≥ selected year)

Rating ranges (2–5, 5–7, 7+)

Rating input auto-disabled for books without rating data

🪟 Detailed Content Popup

Clicking an explore card opens a rich detail popup with:

Large cover image

Summary description

Year, genre, duration/page count

Status controls:

Watched / To Watch

Read / To Read

Rating system (1–10)

Add to custom lists

Comment sub-popup

🧩 Technical Challenge
Keeping popup state consistent after user actions.

✅ Solution
All interactions are stored in Activity and ActivityDetail models.
Popup content is preloaded per user on open.

📂 User Library (Kütüphanem)

Tabbed interface:

Watched

To Watch

Read

To Read

Custom Lists

📝 Custom Lists

Users can:

Create lists with emoji + name

Add movies/books

View lists inside popups

Maintain clean content separation

🔔 Notifications System

Homepage notification bell supports:

New followers

Likes

Comments

Fixed Issues

Bell rendering on wrong pages

Duplicate avatar bug

Dropdown positioning conflicts

📰 Activity Feed

Instagram/Facebook-style feed displaying:

User avatar (with fallback)

Cover image

Activity title & summary

Live like counter

Comment panel

Optimizations

Unified avatar fallback logic

Centralized activity logging for real-time consistency

🛠️ Technology Stack
Backend

Python

Django 5.2

SQLite3 (development)

Frontend

Django Templates

HTML / CSS

JavaScript (static/library/library.js)

Bootstrap

External APIs

TMDB API – Movie data

Open Library API – Book data

🧱 Project Architecture
Apps

accounts – Authentication, profiles, follows, activities, library

explore – Movie & book discovery

core – External API clients

Key Models

User (Django default)

Profile

Activity

ActivityDetail

LibraryItem

CustomList

Follow

Notification

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/Bou-eng/social-library.git
cd social-library

2️⃣ Create a Virtual Environment
python -m venv venv


Activate it:

Windows

venv\Scripts\activate


macOS / Linux

source venv/bin/activate

3️⃣ Install Django & Dependencies
pip install django
pip install -r requirements.txt


If requirements.txt is missing:

pip install django requests

4️⃣ Run Database Migrations
python manage.py migrate

5️⃣ Create a Superuser (Optional)
python manage.py createsuperuser

6️⃣ Run the Development Server
python manage.py runserver


Open your browser and go to:

http://127.0.0.1:8000/

🌍 Development Notes

Language: Turkish (LANGUAGE_CODE = 'tr')

Debug mode enabled

Media files stored in /media/

Local email testing via smtp4dev

🧪 Known Challenges & Solutions
Problem	Solution
Duplicate avatars	Unified avatar rendering
API images not visible	CSS fix with object-fit: cover
Carousel drag issues	Replaced with responsive grid
Broken notification bell	Conditional homepage rendering
🔮 Future Improvements

Production-grade email service

Performance optimizations

Recommendation system (ML-based)

User-to-user messaging

Real-time notifications

📚 References

Django Documentation

TMDB API Docs

Open Library API Docs

Bootstrap Documentation

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

