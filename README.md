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
git clone https://github.com/your-username/social-library.git
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

And here are some pictures of the project:
![WhatsApp Image 2026-01-29 at 7 05 43 PM (1)](https://github.com/user-attachments/assets/652d2001-1c44-4cd8-94d1-09a121d96c57)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (4)](https://github.com/user-attachments/assets/f2e8131a-d2f3-458c-b04f-79cc0abddb9b)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (3)](https://github.com/user-attachments/assets/2e2425df-b2cb-47d0-999d-283273d8200a)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (2)](https://github.com/user-attachments/assets/761d8f75-7b0e-445f-be89-dccfcffd279b)

![WhatsApp Image 2026-01-29 at 7 05 43 PM (6)](https://github.com/user-attachments/assets/5b8c6a3d-a4b0-478e-bfe8-98ffdfd25c03)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (5)](https://github.com/user-attachments/assets/e7677e1e-53b6-47b8-a012-a13848c76ce6)
![WhatsApp Image 2026-01-29 at 7 05 43 PM](https://github.com/user-attachments/assets/e5fdd2d9-4f49-43a9-b2e3-84e2bba4bdad)
![WhatsApp Image 2026-01-29 at 7 05 43 PM (7)](https://github.com/user-attachments/assets/32784ad7-9ddf-4c93-9991-63935f75647d)

![WhatsApp Image 2026-01-29 at 7 05 44 PM (3)](https://github.com/user-attachments/assets/92d1066f-04a6-46be-af33-9b3b74cc7866)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (2)](https://github.com/user-attachments/assets/132b71fa-edbe-4930-b05d-fbb107e85878)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (1)](https://github.com/user-attachments/assets/e58fea64-d96a-41d0-b307-f63abc869386)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (4)](https://github.com/user-attachments/assets/0ffcb047-fd0c-4a37-8718-4c3b87465f56)


![WhatsApp Image 2026-01-29 at 7 05 44 PM (5)](https://github.com/user-attachments/assets/1ec483a2-45c7-4e66-bf0c-eadd56ee6840)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (8)](https://github.com/user-attachments/assets/6c1be84a-859d-45b4-9b65-4fd0014eafc6)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (7)](https://github.com/user-attachments/assets/18494407-fca8-4554-9995-2f9894682505)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (6)](https://github.com/user-attachments/assets/d72bbb2b-e460-4e68-a470-a4768e350559)



![WhatsApp Image 2026-01-29 at 7 05 44 PM (9)](https://github.com/user-attachments/assets/9f550702-3ecb-4964-8839-75d35ad551f5)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (12)](https://github.com/user-attachments/assets/d1fd3226-63fa-47a1-876b-93f46db7930a)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (11)](https://github.com/user-attachments/assets/64626455-a5d0-4bda-864c-e012be94b7a9)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (10)](https://github.com/user-attachments/assets/20d6fc78-48a2-4092-9762-894735b2d0f8)


![WhatsApp Image 2026-01-29 at 7 05 44 PM (13)](https://github.com/user-attachments/assets/0d3cf46a-ed64-4180-b757-255d0026b83a)
![WhatsApp Image 2026-01-29 at 7 05 44 PM](https://github.com/user-attachments/assets/dff9062d-255e-49ab-9442-357c077a0d1b)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (15)](https://github.com/user-attachments/assets/238e0968-a8d5-4562-bcd9-212826d71d72)
![WhatsApp Image 2026-01-29 at 7 05 44 PM (14)](https://github.com/user-attachments/assets/007b1224-3616-4be4-9d03-8fe08561e26b)



