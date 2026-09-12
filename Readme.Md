# Bank Transaction API

Ushbu loyiha Django REST Framework asosida ishlab chiqilgan REST API bo‘lib, foydalanuvchilar va bank tranzaksiyalarini boshqarish uchun mo‘ljallangan.

## Loyiha haqida

Loyiha quyidagi imkoniyatlarni taqdim etadi:

- Foydalanuvchini ro‘yxatdan o‘tkazish
- Tizimga kirish (JWT Authentication)
- Tranzaksiya yaratish
- Tranzaksiyalar ro‘yxatini ko‘rish
- Bitta tranzaksiya ma'lumotlarini olish
- Tranzaksiyani tahrirlash
- Tranzaksiyani o‘chirish
- Tranzaksiyalarni filtrlash va qidirish

## Texnologiyalar

- Python 3
- Django
- Django REST Framework
- SQLite3
- Simple JWT
- django-filter

## Loyiha tuzilishi

project/
│── accounts/
│── transactions/
│── config/
│── manage.py
│── requirements.txt
│── db.sqlite3
## O‘rnatish

Repository'ni yuklab oling:

git clone <repository_url>
Virtual muhit yarating:

python -m venv venv
Virtual muhitni faollashtiring.

Windows:

venv\Scripts\activate
Linux/macOS:

source venv/bin/activate
Kerakli kutubxonalarni o‘rnating:

pip install -r requirements.txt
Migratsiyalarni bajaring:

python manage.py migrate
Serverni ishga tushiring:

python manage.py runserver
## Autentifikatsiya

Loyihada JWT Authentication qo‘llanilgan.

Himoyalangan endpointlarga murojaat qilish uchun Access Token quyidagi ko‘rinishda yuboriladi:

Authorization: Bearer <access_token>
## API Endpointlari

### Authentication

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | /register/ | Foydalanuvchini ro‘yxatdan o‘tkazish |
| POST | /login/ | Tizimga kirish |

### Transactions

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | /transactions/ | Tranzaksiyalar ro‘yxati |
| POST | /transactions/ | Yangi tranzaksiya yaratish |
| GET | /transactions/<id>/ | Bitta tranzaksiyani ko‘rish |
| PUT | /transactions/<id>/ | Tranzaksiyani tahrirlash |
| DELETE | /transactions/<id>/ | Tranzaksiyani o‘chirish |

## Ma'lumotlar bazasi

Loyihada standart SQLite ma'lumotlar bazasidan foydalanilgan.

## Muallif

Ziyovuddin Abdullaev

Django REST Framework asosida ishlab chiqilgan imtihon loyihasi.