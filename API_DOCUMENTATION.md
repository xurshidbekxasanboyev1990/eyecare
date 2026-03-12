# 📱 EyeCare Mobile API Documentation

**Base URL:** `http://192.168.213.3:8000/api/v1`

**Swagger UI:** `http://192.168.213.3:8000/docs`

**ReDoc:** `http://192.168.213.3:8000/redoc`

---

## 📋 Table of Contents

1. [Authentication](#-authentication)
2. [Users](#-users)
3. [Eye Tests](#-eye-tests)
4. [Test Sessions](#-test-sessions)
5. [Test Results](#-test-results)
6. [Doctors](#-doctors)
7. [Appointments](#-appointments)
8. [Clinics](#-clinics)
9. [Articles](#-articles)
10. [Notifications](#-notifications)
11. [Response Formats](#-response-formats)

---

## 🔐 Authentication

### Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "phone": "+998901234567",
  "password": "securePassword123",
  "full_name": "Ism Familiya",
  "birth_date": "1990-01-15",
  "gender": "male"  // male, female
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ro'yxatdan o'tish muvaffaqiyatli",
  "data": {
    "user": {
      "id": "uuid",
      "phone": "+998901234567",
      "full_name": "Ism Familiya",
      "created_at": "2026-02-05T12:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

---

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "phone": "+998901234567",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

---

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### Send SMS Code (Phone Verification)
```http
POST /auth/send-code
Content-Type: application/json

{
  "phone": "+998901234567"
}
```

---

### Verify SMS Code
```http
POST /auth/verify-code
Content-Type: application/json

{
  "phone": "+998901234567",
  "code": "123456"
}
```

---

### Logout
```http
POST /auth/logout
Authorization: Bearer {access_token}
```

---

## 👤 Users

### Get Current User Profile
```http
GET /users/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "phone": "+998901234567",
    "full_name": "Ism Familiya",
    "birth_date": "1990-01-15",
    "gender": "male",
    "avatar_url": "https://...",
    "region": "Toshkent",
    "language": "uz",
    "notifications_enabled": true,
    "created_at": "2026-01-01T00:00:00Z",
    "last_test_at": "2026-02-01T00:00:00Z",
    "test_count": 5
  }
}
```

---

### Update Profile
```http
PUT /users/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Yangi Ism",
  "birth_date": "1990-05-20",
  "region": "Samarqand",
  "language": "uz",
  "notifications_enabled": true
}
```

---

### Upload Avatar
```http
POST /users/me/avatar
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

avatar: [file]
```

---

### Delete Account
```http
DELETE /users/me
Authorization: Bearer {access_token}
```

---

### Get User Statistics
```http
GET /users/me/statistics
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_tests": 15,
    "tests_this_month": 3,
    "average_visual_acuity": "20/25",
    "last_test_date": "2026-02-01",
    "test_history": [
      {
        "date": "2026-02-01",
        "type": "visual_acuity",
        "result": "20/25"
      }
    ],
    "recommendations_count": 2,
    "appointments_count": 1
  }
}
```

---

## 👁 Eye Tests

### Get All Test Types
```http
GET /tests/types
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "visual_acuity",
      "name": "Ko'rish o'tkirligi",
      "name_en": "Visual Acuity",
      "description": "Snellen chart yordamida ko'rish o'tkirligini aniqlash",
      "icon": "👁",
      "duration_minutes": 5,
      "requires_distance": true,
      "recommended_distance_cm": 500,
      "instructions": [
        "5 metr masofada turing",
        "Avval o'ng ko'zni yoping",
        "Harflarni aniqlang"
      ]
    },
    {
      "id": "color_blindness",
      "name": "Rang ko'rish",
      "name_en": "Color Blindness",
      "description": "Ishihara plitalari bilan rang ko'rish tekshiruvi",
      "icon": "🎨",
      "duration_minutes": 3,
      "requires_distance": false
    },
    {
      "id": "contrast",
      "name": "Kontrast sezgirligi",
      "name_en": "Contrast Sensitivity",
      "icon": "🔲",
      "duration_minutes": 4
    },
    {
      "id": "astigmatism",
      "name": "Astigmatizm",
      "name_en": "Astigmatism",
      "icon": "📐",
      "duration_minutes": 3
    },
    {
      "id": "amsler",
      "name": "Amsler panjarasi",
      "name_en": "Amsler Grid",
      "description": "Makula degeneratsiyasini aniqlash",
      "icon": "📊",
      "duration_minutes": 2
    },
    {
      "id": "near_vision",
      "name": "Yaqin ko'rish",
      "name_en": "Near Vision",
      "icon": "📖",
      "duration_minutes": 3
    },
    {
      "id": "dry_eye",
      "name": "Quruq ko'z",
      "name_en": "Dry Eye",
      "icon": "💧",
      "duration_minutes": 5
    },
    {
      "id": "peripheral",
      "name": "Periferik ko'rish",
      "name_en": "Peripheral Vision",
      "icon": "👀",
      "duration_minutes": 4
    }
  ]
}
```

---

### Get Test Details
```http
GET /tests/types/{test_type}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "visual_acuity",
    "name": "Ko'rish o'tkirligi testi",
    "description": "Bu test Snellen chart yordamida...",
    "detailed_instructions": "...",
    "preparation": [
      "Yaxshi yoritilgan xonada bo'ling",
      "Ko'zoynakingizni taqing (agar bor bo'lsa)"
    ],
    "chart_data": {
      "lines": [
        {"size": "20/200", "letters": "E"},
        {"size": "20/100", "letters": "FP"},
        {"size": "20/70", "letters": "TOZ"},
        {"size": "20/50", "letters": "LPED"},
        {"size": "20/40", "letters": "PECFD"},
        {"size": "20/30", "letters": "EDFCZP"},
        {"size": "20/25", "letters": "FELOPZD"},
        {"size": "20/20", "letters": "DEFPOTEC"},
        {"size": "20/15", "letters": "LEFODPCT"},
        {"size": "20/10", "letters": "FDPLTCEO"}
      ]
    }
  }
}
```

---

## 📝 Test Sessions

### Start New Test Session
```http
POST /tests/sessions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "test_types": ["visual_acuity", "color_blindness"],
  "device_info": {
    "model": "iPhone 14",
    "os": "iOS 17.2",
    "screen_size": "6.1 inch",
    "screen_ppi": 460
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "status": "in_progress",
    "tests": [
      {
        "type": "visual_acuity",
        "order": 1,
        "status": "pending"
      },
      {
        "type": "color_blindness",
        "order": 2,
        "status": "pending"
      }
    ],
    "created_at": "2026-02-05T12:00:00Z"
  }
}
```

---

### Get Session Status
```http
GET /tests/sessions/{session_id}
Authorization: Bearer {access_token}
```

---

### Submit Test Result
```http
POST /tests/sessions/{session_id}/results
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "test_type": "visual_acuity",
  "eye_side": "right",  // right, left, both
  "score": "20/25",
  "answers": [
    {"line": 1, "correct": true},
    {"line": 2, "correct": true},
    {"line": 3, "correct": true},
    {"line": 4, "correct": false}
  ],
  "duration_seconds": 180,
  "distance_cm": 500
}
```

---

### Complete Session
```http
POST /tests/sessions/{session_id}/complete
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "status": "completed",
    "summary": {
      "overall_score": 85,
      "risk_level": "low",  // low, medium, high
      "results": [
        {
          "test_type": "visual_acuity",
          "right_eye": "20/25",
          "left_eye": "20/30",
          "status": "normal"
        },
        {
          "test_type": "color_blindness",
          "score": "normal",
          "status": "normal"
        }
      ],
      "recommendations": [
        {
          "priority": "info",
          "message": "Ko'rish o'tkirligingiz yaxshi darajada",
          "action": null
        },
        {
          "priority": "warning",
          "message": "Chap ko'zingiz biroz zaif. Oftalmologga murojaat qilishni tavsiya etamiz",
          "action": "book_appointment"
        }
      ]
    },
    "completed_at": "2026-02-05T12:15:00Z"
  }
}
```

---

### Get Session History
```http
GET /tests/sessions
Authorization: Bearer {access_token}
Query params:
  - page: 1
  - limit: 10
  - from_date: 2026-01-01
  - to_date: 2026-02-05
```

---

## 📊 Test Results

### Get All Results
```http
GET /tests/results
Authorization: Bearer {access_token}
Query params:
  - test_type: visual_acuity (optional)
  - from_date: 2026-01-01 (optional)
  - to_date: 2026-02-05 (optional)
  - limit: 20
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid",
        "session_id": "uuid",
        "test_type": "visual_acuity",
        "eye_side": "right",
        "score": "20/25",
        "status": "normal",
        "created_at": "2026-02-05T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

---

### Get Single Result
```http
GET /tests/results/{result_id}
Authorization: Bearer {access_token}
```

---

### Get Result Comparison (Progress Over Time)
```http
GET /tests/results/compare
Authorization: Bearer {access_token}
Query params:
  - test_type: visual_acuity
  - period: 6months  // 1month, 3months, 6months, 1year
```

**Response:**
```json
{
  "success": true,
  "data": {
    "test_type": "visual_acuity",
    "trend": "stable",  // improving, stable, declining
    "data_points": [
      {"date": "2025-08-01", "right_eye": "20/30", "left_eye": "20/35"},
      {"date": "2025-10-15", "right_eye": "20/25", "left_eye": "20/30"},
      {"date": "2026-01-10", "right_eye": "20/25", "left_eye": "20/30"},
      {"date": "2026-02-05", "right_eye": "20/25", "left_eye": "20/25"}
    ],
    "analysis": "Oxirgi 6 oyda ko'rish o'tkirligingiz barqaror"
  }
}
```

---

### Download Result as PDF
```http
GET /tests/results/{result_id}/pdf
Authorization: Bearer {access_token}
```

---

## 👨‍⚕️ Doctors

### Get All Doctors
```http
GET /doctors
Query params:
  - region: Toshkent (optional)
  - specialization: oftalmolog (optional)
  - rating_min: 4.0 (optional)
  - page: 1
  - limit: 20
```

**Response:**
```json
{
  "success": true,
  "data": {
    "doctors": [
      {
        "id": "uuid",
        "full_name": "Dr. Karimov Anvar",
        "specialization": "Oftalmolog",
        "experience_years": 15,
        "rating": 4.8,
        "reviews_count": 124,
        "avatar_url": "https://...",
        "clinic": {
          "id": "uuid",
          "name": "EyeCare Klinikasi",
          "address": "Toshkent, Yunusobod tumani"
        },
        "consultation_price": 150000,
        "available_today": true
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45
    }
  }
}
```

---

### Get Doctor Details
```http
GET /doctors/{doctor_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "full_name": "Dr. Karimov Anvar",
    "specialization": "Oftalmolog",
    "bio": "15 yillik tajribaga ega ko'z shifokori...",
    "education": [
      "Toshkent Tibbiyot Akademiyasi (2005-2011)",
      "IISOS ko'z kasalliklari bo'yicha malaka oshirish (2015)"
    ],
    "experience_years": 15,
    "languages": ["uz", "ru", "en"],
    "rating": 4.8,
    "reviews_count": 124,
    "avatar_url": "https://...",
    "clinic": {
      "id": "uuid",
      "name": "EyeCare Klinikasi",
      "address": "Toshkent, Yunusobod tumani, Amir Temur ko'chasi 45",
      "phone": "+998712345678",
      "location": {
        "lat": 41.311081,
        "lng": 69.240562
      }
    },
    "services": [
      {"name": "Konsultatsiya", "price": 150000},
      {"name": "Ko'z diagnostikasi", "price": 300000},
      {"name": "Lazer korrektsiya", "price": 5000000}
    ],
    "working_hours": {
      "monday": {"start": "09:00", "end": "18:00"},
      "tuesday": {"start": "09:00", "end": "18:00"},
      "wednesday": {"start": "09:00", "end": "18:00"},
      "thursday": {"start": "09:00", "end": "18:00"},
      "friday": {"start": "09:00", "end": "16:00"},
      "saturday": {"start": "10:00", "end": "14:00"},
      "sunday": null
    }
  }
}
```

---

### Get Doctor Available Slots
```http
GET /doctors/{doctor_id}/slots
Query params:
  - date: 2026-02-10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "date": "2026-02-10",
    "slots": [
      {"time": "09:00", "available": true},
      {"time": "09:30", "available": true},
      {"time": "10:00", "available": false},
      {"time": "10:30", "available": true},
      {"time": "11:00", "available": true}
    ]
  }
}
```

---

### Get Doctor Reviews
```http
GET /doctors/{doctor_id}/reviews
Query params:
  - page: 1
  - limit: 10
```

---

### Submit Doctor Review
```http
POST /doctors/{doctor_id}/reviews
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "rating": 5,
  "comment": "Juda yaxshi shifokor, tavsiya qilaman"
}
```

---

## 📅 Appointments

### Create Appointment
```http
POST /appointments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "doctor_id": "uuid",
  "scheduled_at": "2026-02-10T10:30:00Z",
  "session_id": "uuid",  // optional - test natijalarini biriktirish
  "notes": "Ko'rish tekshiruvi uchun"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "doctor": {
      "id": "uuid",
      "full_name": "Dr. Karimov Anvar",
      "phone": "+998901234567"
    },
    "scheduled_at": "2026-02-10T10:30:00Z",
    "status": "pending",
    "confirmation_code": "ABC123",
    "created_at": "2026-02-05T12:00:00Z"
  }
}
```

---

### Get My Appointments
```http
GET /appointments
Authorization: Bearer {access_token}
Query params:
  - status: pending,confirmed (optional)
  - from_date: 2026-02-01 (optional)
```

---

### Get Appointment Details
```http
GET /appointments/{appointment_id}
Authorization: Bearer {access_token}
```

---

### Cancel Appointment
```http
DELETE /appointments/{appointment_id}
Authorization: Bearer {access_token}

{
  "reason": "Bandlik sababli"
}
```

---

### Reschedule Appointment
```http
PUT /appointments/{appointment_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "scheduled_at": "2026-02-12T14:00:00Z"
}
```

---

## 🏥 Clinics

### Get All Clinics
```http
GET /clinics
Query params:
  - region: Toshkent (optional)
  - lat: 41.311081 (optional)
  - lng: 69.240562 (optional)
  - radius_km: 10 (optional)
  - page: 1
  - limit: 20
```

---

### Get Clinic Details
```http
GET /clinics/{clinic_id}
```

---

### Get Nearest Clinics
```http
GET /clinics/nearest
Query params:
  - lat: 41.311081
  - lng: 69.240562
  - limit: 5
```

---

## 📰 Articles

### Get All Articles
```http
GET /articles
Query params:
  - category: eye_health (optional)
  - page: 1
  - limit: 10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "articles": [
      {
        "id": "uuid",
        "title": "Ko'zni qanday parvarish qilish kerak",
        "summary": "Ko'z salomatligini saqlash bo'yicha maslahatlar...",
        "image_url": "https://...",
        "category": "eye_health",
        "read_time_minutes": 5,
        "views_count": 1234,
        "created_at": "2026-02-01T00:00:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

---

### Get Article Details
```http
GET /articles/{article_id}
```

---

### Get Featured Articles
```http
GET /articles/featured
```

---

## 🔔 Notifications

### Get Notifications
```http
GET /notifications
Authorization: Bearer {access_token}
Query params:
  - unread_only: true (optional)
  - page: 1
  - limit: 20
```

---

### Mark Notification as Read
```http
PUT /notifications/{notification_id}/read
Authorization: Bearer {access_token}
```

---

### Mark All as Read
```http
PUT /notifications/read-all
Authorization: Bearer {access_token}
```

---

### Update Notification Settings
```http
PUT /notifications/settings
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "push_enabled": true,
  "sms_enabled": false,
  "email_enabled": true,
  "reminder_before_hours": 24,
  "test_reminders": true,
  "news_updates": false
}
```

---

## 📋 Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Muvaffaqiyatli",
  "data": {...}
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Telefon raqam noto'g'ri formatda",
    "details": {
      "field": "phone",
      "value": "123"
    }
  }
}
```

### Error Codes
| Code | Description |
|------|-------------|
| `UNAUTHORIZED` | Token noto'g'ri yoki muddati tugagan |
| `FORBIDDEN` | Ruxsat yo'q |
| `NOT_FOUND` | Topilmadi |
| `VALIDATION_ERROR` | Ma'lumotlar noto'g'ri |
| `RATE_LIMITED` | Juda ko'p so'rov |
| `SERVER_ERROR` | Server xatosi |

---

## 🔧 Headers

### Required Headers
```
Content-Type: application/json
Accept: application/json
Accept-Language: uz  // uz, ru, en
```

### Authentication Header
```
Authorization: Bearer {access_token}
```

### Optional Headers
```
X-Device-ID: unique-device-id
X-App-Version: 1.0.0
X-Platform: android  // android, ios
```

---

## 📱 WebSocket Events (Real-time)

### Connect
```
ws://192.168.213.3:8000/ws?token={access_token}
```

### Events
```json
// Test session update
{
  "event": "session_update",
  "data": {
    "session_id": "uuid",
    "status": "completed"
  }
}

// Appointment reminder
{
  "event": "appointment_reminder",
  "data": {
    "appointment_id": "uuid",
    "scheduled_at": "2026-02-10T10:30:00Z",
    "doctor_name": "Dr. Karimov"
  }
}

// New notification
{
  "event": "notification",
  "data": {
    "id": "uuid",
    "type": "test_reminder",
    "title": "Test eslatmasi",
    "body": "Ko'z testini o'tkazish vaqti keldi"
  }
}
```

---

## 📊 Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/auth/*` | 10 requests/minute |
| `/tests/*` | 60 requests/minute |
| `/users/*` | 30 requests/minute |
| Other | 100 requests/minute |

---

## 🔒 Security Notes

1. **Token Expiry**: Access token 1 soatda tugaydi
2. **Refresh Token**: Refresh token 30 kunda tugaydi
3. **HTTPS**: Production'da faqat HTTPS ishlatiladi
4. **Rate Limiting**: Limitdan oshganda 429 qaytadi

---

## 📞 Support

- **API Issues**: api@eyecare.uz
- **Documentation**: docs@eyecare.uz
- **Telegram**: @eyecare_support

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-05
