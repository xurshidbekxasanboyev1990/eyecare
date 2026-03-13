# EyeCare Backend - To'liq Texnik Spetsifikatsiya

## 📋 Loyiha Haqida

**EyeCare** - Professional ko'z tekshiruvi PWA ilovasi uchun backend API servisi. Bu hujjat backend qismini noldan yozish uchun barcha kerakli ma'lumotlarni o'z ichiga oladi.

---

## 🏗️ Texnologiya Stack

### Asosiy
- **Runtime**: Node.js 20+ (yoki Python 3.11+ / Go 1.21+)
- **Framework**: Express.js / Fastify (yoki FastAPI / Gin)
- **Database**: PostgreSQL 16+ (asosiy) + Redis 7+ (cache/sessions)
- **ORM**: Prisma / Drizzle (yoki SQLAlchemy / GORM)

### Qo'shimcha
- **Authentication**: JWT (Access + Refresh tokens)
- **File Storage**: MinIO / AWS S3 (PDF va rasmlar uchun)
- **Queue**: BullMQ / Redis Queue (background jobs)
- **Telegram Bot**: node-telegram-bot-api / grammy
- **Email**: Nodemailer / Resend
- **SMS**: Eskiz.uz / PlayMobile API
- **Logging**: Pino / Winston
- **Validation**: Zod / Joi
- **Documentation**: Swagger/OpenAPI 3.0

---

## 📊 Ma'lumotlar Bazasi Sxemasi

### 1. Users (Foydalanuvchilar)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    avatar_url TEXT,
    language VARCHAR(5) DEFAULT 'uz',
    timezone VARCHAR(50) DEFAULT 'Asia/Tashkent',
    
    -- Authentication
    password_hash VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(6),
    verification_expires_at TIMESTAMP,
    
    -- Settings
    notifications_enabled BOOLEAN DEFAULT TRUE,
    reminder_days INTEGER DEFAULT 180,
    
    -- Metadata
    last_login_at TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);
```

### 2. Admins (Administratorlar)

```sql
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin' CHECK (role IN ('super_admin', 'admin', 'moderator')),
    
    -- Permissions (JSON)
    permissions JSONB DEFAULT '{}',
    
    -- Security
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(45),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    
    -- 2FA
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Test Sessions (Test Sessiyalari)

```sql
CREATE TABLE test_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session Info
    session_token VARCHAR(64) UNIQUE NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Device Info
    device_type VARCHAR(20), -- mobile, tablet, desktop
    browser VARCHAR(50),
    os VARCHAR(50),
    screen_width INTEGER,
    screen_height INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Distance Calibration
    calibrated_distance_cm INTEGER,
    ipd_mm DECIMAL(4,2), -- Inter-pupillary distance
    
    -- Status
    status VARCHAR(20) DEFAULT 'in_progress' 
        CHECK (status IN ('in_progress', 'completed', 'abandoned', 'expired')),
    
    -- PDF
    pdf_url TEXT,
    pdf_generated_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_sessions_user_id ON test_sessions(user_id);
CREATE INDEX idx_test_sessions_status ON test_sessions(status);
CREATE INDEX idx_test_sessions_created_at ON test_sessions(created_at DESC);
```

### 4. Test Results (Test Natijalari)

```sql
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES test_sessions(id) ON DELETE CASCADE,
    
    -- Test Identification
    test_type VARCHAR(30) NOT NULL,
    test_order INTEGER NOT NULL,
    
    -- Results
    score VARCHAR(20),
    status VARCHAR(20) CHECK (status IN ('normal', 'warning', 'concern', 'skipped')),
    details TEXT,
    raw_data JSONB, -- Original test data
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Distance during test
    distance_cm INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_results_session_id ON test_results(session_id);
CREATE INDEX idx_test_results_test_type ON test_results(test_type);

-- Test Types ENUM reference:
-- 'visual_acuity'      - Ko'rish O'tkirligi (Snellen)
-- 'color_blindness'    - Rang Ajratish (Ishihara)
-- 'amsler_grid'        - Amsler Panjarasi
-- 'contrast'           - Kontrast Sezgirligi
-- 'astigmatism'        - Astigmatizm
-- 'duochrome'          - Duoxrom
-- 'near_vision'        - Yaqindan Ko'rish
-- 'red_desaturation'   - Qizil Desaturatsiya
-- 'perimetry'          - Perimetriya
-- 'dry_eye'            - Quruq Ko'z Sindromi
```

### 5. Doctors (Shifokorlar)

```sql
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    full_name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100) DEFAULT 'Oftalmolog',
    experience VARCHAR(50),
    bio TEXT,
    avatar_url TEXT,
    
    -- Contact
    phone VARCHAR(20),
    email VARCHAR(255),
    telegram VARCHAR(50),
    
    -- Location
    clinic_name VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    district VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Schedule
    work_hours VARCHAR(100),
    work_days VARCHAR(50), -- e.g., "1,2,3,4,5" (Mon-Fri)
    
    -- Pricing
    consultation_price INTEGER,
    currency VARCHAR(3) DEFAULT 'UZS',
    
    -- Rating
    rating DECIMAL(2,1) DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0, -- For ordering
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doctors_is_active ON doctors(is_active);
CREATE INDEX idx_doctors_city ON doctors(city);
```

### 6. Doctor Reviews (Shifokor Sharhlari)

```sql
CREATE TABLE doctor_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id UUID REFERENCES doctors(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    
    -- Moderation
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES admins(id),
    approved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. Appointments (Uchrashuvlar)

```sql
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(id) ON DELETE CASCADE,
    session_id UUID REFERENCES test_sessions(id),
    
    -- Timing
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled', 'no_show')),
    
    -- Notes
    user_notes TEXT,
    doctor_notes TEXT,
    
    -- Reminders
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_sent_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_appointments_user_id ON appointments(user_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_appointments_scheduled_at ON appointments(scheduled_at);
```

### 8. App Settings (Ilova Sozlamalari)

```sql
CREATE TABLE app_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50),
    is_public BOOLEAN DEFAULT FALSE,
    
    updated_by UUID REFERENCES admins(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default settings
INSERT INTO app_settings (key, value, category, is_public) VALUES
('app_name', '"EyeCare"', 'general', true),
('app_version', '"1.0.0"', 'general', true),
('maintenance_mode', 'false', 'general', true),
('default_language', '"uz"', 'general', true),
('supported_languages', '["uz", "ru", "en"]', 'general', true),
('test_distance_cm', '{"visualAcuity": 300, "colorBlindness": 75, "amsler": 30, "contrast": 100, "astigmatism": 50, "duochrome": 50, "nearVision": 35, "redDesaturation": 50, "perimetry": 50, "dryEye": 40}', 'tests', false),
('enabled_tests', '["visualAcuity", "colorBlindness", "amsler", "contrast", "astigmatism", "duochrome", "nearVision", "redDesaturation", "perimetry", "dryEye"]', 'tests', false);
```

### 9. Notifications (Bildirishnomalar)

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    type VARCHAR(30) NOT NULL, -- 'reminder', 'result', 'appointment', 'promotion'
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB,
    
    -- Delivery
    channel VARCHAR(20) NOT NULL, -- 'push', 'telegram', 'sms', 'email'
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'read')),
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
```

### 10. Telegram Bot Sessions

```sql
CREATE TABLE telegram_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    
    -- State
    current_state VARCHAR(50) DEFAULT 'idle',
    state_data JSONB,
    
    -- Chat Info
    chat_id BIGINT NOT NULL,
    username VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    language_code VARCHAR(5),
    
    -- Stats
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_telegram_sessions_telegram_id ON telegram_sessions(telegram_id);
```

### 11. Activity Logs (Faoliyat Loglari)

```sql
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Actor
    actor_type VARCHAR(20) NOT NULL, -- 'user', 'admin', 'system', 'bot'
    actor_id UUID,
    
    -- Action
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    
    -- Details
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_logs_actor ON activity_logs(actor_type, actor_id);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at DESC);

-- Partitioning by month for performance
-- CREATE TABLE activity_logs_2026_01 PARTITION OF activity_logs
--     FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

---

## 🔌 API Endpoints

### Base URL
```
Production: https://api.eyecare.uz/v1
Development: http://localhost:3000/api/v1
```

### Response Format
```json
{
    "success": true,
    "data": { ... },
    "meta": {
        "page": 1,
        "limit": 20,
        "total": 100,
        "totalPages": 5
    },
    "timestamp": "2026-01-24T12:00:00Z"
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Validation failed",
        "details": [
            { "field": "email", "message": "Invalid email format" }
        ]
    },
    "timestamp": "2026-01-24T12:00:00Z"
}
```

---

### 🔐 Authentication Endpoints

#### POST /auth/register
Yangi foydalanuvchi ro'yxatdan o'tkazish

**Request:**
```json
{
    "phone": "+998901234567",
    "full_name": "Alisher Karimov",
    "password": "securePassword123",
    "birth_date": "1990-05-15",
    "gender": "male"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "uuid",
            "phone": "+998901234567",
            "full_name": "Alisher Karimov",
            "is_verified": false
        },
        "message": "Tasdiqlash kodi yuborildi"
    }
}
```

#### POST /auth/verify
Telefon raqamini tasdiqlash

**Request:**
```json
{
    "phone": "+998901234567",
    "code": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "expires_in": 3600,
        "user": { ... }
    }
}
```

#### POST /auth/login
Tizimga kirish

**Request:**
```json
{
    "phone": "+998901234567",
    "password": "securePassword123"
}
```

#### POST /auth/login/telegram
Telegram orqali kirish

**Request:**
```json
{
    "telegram_id": 123456789,
    "hash": "telegram_auth_hash",
    "auth_date": 1706097600
}
```

#### POST /auth/refresh
Token yangilash

**Request:**
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST /auth/logout
Tizimdan chiqish

**Headers:** `Authorization: Bearer <token>`

#### POST /auth/forgot-password
Parolni tiklash

**Request:**
```json
{
    "phone": "+998901234567"
}
```

#### POST /auth/reset-password
Yangi parol o'rnatish

**Request:**
```json
{
    "phone": "+998901234567",
    "code": "123456",
    "new_password": "newSecurePassword123"
}
```

---

### 👤 User Endpoints

#### GET /users/me
Joriy foydalanuvchi ma'lumotlari

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "phone": "+998901234567",
        "email": "user@example.com",
        "full_name": "Alisher Karimov",
        "birth_date": "1990-05-15",
        "gender": "male",
        "avatar_url": "https://...",
        "language": "uz",
        "notifications_enabled": true,
        "reminder_days": 180,
        "stats": {
            "total_tests": 5,
            "last_test_date": "2026-01-20T10:00:00Z"
        },
        "created_at": "2025-01-01T00:00:00Z"
    }
}
```

#### PATCH /users/me
Foydalanuvchi ma'lumotlarini yangilash

**Request:**
```json
{
    "full_name": "Alisher Karimov",
    "email": "new@example.com",
    "language": "ru",
    "notifications_enabled": false
}
```

#### DELETE /users/me
Hisobni o'chirish

#### POST /users/me/avatar
Avatar yuklash

**Request:** `multipart/form-data` with `avatar` file

---

### 🧪 Test Session Endpoints

#### POST /tests/sessions
Yangi test sessiyasini boshlash

**Headers:** `Authorization: Bearer <token>` (optional - guest allowed)

**Request:**
```json
{
    "device_info": {
        "type": "mobile",
        "browser": "Chrome",
        "os": "Android 14",
        "screen_width": 1080,
        "screen_height": 2400
    },
    "calibration": {
        "distance_cm": 50,
        "ipd_mm": 63.5
    }
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "session_id": "uuid",
        "session_token": "abc123...",
        "tests": [
            {
                "type": "visual_acuity",
                "name": "Ko'rish O'tkirligi",
                "order": 1,
                "required_distance_cm": 300,
                "estimated_duration_seconds": 120
            },
            ...
        ],
        "expires_at": "2026-01-24T14:00:00Z"
    }
}
```

#### GET /tests/sessions/:id
Sessiya ma'lumotlarini olish

#### POST /tests/sessions/:id/results
Test natijasini saqlash

**Request:**
```json
{
    "test_type": "visual_acuity",
    "test_order": 1,
    "score": "20/25",
    "status": "normal",
    "details": "O'ng ko'z: 20/20, Chap ko'z: 20/25",
    "raw_data": {
        "right_eye": { "score": "20/20", "line": 8 },
        "left_eye": { "score": "20/25", "line": 7 }
    },
    "duration_seconds": 95,
    "distance_cm": 300
}
```

#### POST /tests/sessions/:id/complete
Sessiyani yakunlash

**Request:**
```json
{
    "completed_tests": 10,
    "total_duration_seconds": 900
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "session_id": "uuid",
        "summary": {
            "overall_status": "warning",
            "tests_completed": 10,
            "concerns": ["color_blindness", "contrast"],
            "recommendations": [
                "Rang ko'rish bo'yicha shifokorga murojaat qiling"
            ]
        },
        "pdf_url": "https://storage.eyecare.uz/reports/uuid.pdf"
    }
}
```

#### GET /tests/sessions/:id/pdf
PDF hisobotni yuklab olish

**Response:** PDF file stream

---

### 📊 Results & History Endpoints

#### GET /results
Foydalanuvchi test tarixi

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20)
- `from_date` (ISO date)
- `to_date` (ISO date)
- `status` (normal, warning, concern)

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "session_id": "uuid",
            "completed_at": "2026-01-20T10:00:00Z",
            "overall_status": "normal",
            "tests_count": 10,
            "duration_seconds": 850,
            "pdf_url": "https://..."
        }
    ],
    "meta": {
        "page": 1,
        "limit": 20,
        "total": 5
    }
}
```

#### GET /results/:sessionId
Bitta sessiyaning to'liq natijalari

**Response:**
```json
{
    "success": true,
    "data": {
        "session": {
            "id": "uuid",
            "completed_at": "2026-01-20T10:00:00Z",
            "duration_seconds": 850,
            "device_type": "mobile"
        },
        "results": [
            {
                "test_type": "visual_acuity",
                "test_name": "Ko'rish O'tkirligi",
                "score": "20/25",
                "status": "normal",
                "details": "O'ng ko'z: 20/20, Chap ko'z: 20/25",
                "duration_seconds": 95
            },
            ...
        ],
        "summary": {
            "overall_status": "warning",
            "concerns": ["contrast"],
            "recommendations": [...]
        },
        "pdf_url": "https://..."
    }
}
```

#### GET /results/stats
Foydalanuvchi statistikasi

**Response:**
```json
{
    "success": true,
    "data": {
        "total_sessions": 5,
        "first_test_date": "2025-06-15T10:00:00Z",
        "last_test_date": "2026-01-20T10:00:00Z",
        "average_duration_seconds": 820,
        "test_frequency": {
            "monthly": 0.8,
            "average_days_between": 45
        },
        "trend": {
            "visual_acuity": "stable",
            "color_blindness": "stable",
            "contrast": "declining"
        },
        "next_recommended_test": "2026-07-20T00:00:00Z"
    }
}
```

---

### 👨‍⚕️ Doctor Endpoints

#### GET /doctors
Shifokorlar ro'yxati

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20)
- `city` (filter by city)
- `specialty` (filter by specialty)
- `min_rating` (minimum rating)
- `lat`, `lng`, `radius_km` (location-based search)
- `sort` (rating, distance, price)

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "full_name": "Dr. Abdullayev Jasur",
            "specialty": "Oftalmolog",
            "experience": "15 yillik tajriba",
            "clinic_name": "Salomatlik Klinikasi",
            "address": "Toshkent sh., Chilonzor t.",
            "phone": "+998711234567",
            "work_hours": "Dush-Juma: 09:00 - 18:00",
            "rating": 4.8,
            "review_count": 124,
            "consultation_price": 150000,
            "distance_km": 2.5
        }
    ],
    "meta": { ... }
}
```

#### GET /doctors/:id
Shifokor haqida to'liq ma'lumot

#### GET /doctors/:id/reviews
Shifokor sharhlari

#### POST /doctors/:id/reviews
Sharh qoldirish

**Request:**
```json
{
    "rating": 5,
    "comment": "Juda yaxshi shifokor, tavsiya qilaman"
}
```

---

### 📅 Appointment Endpoints

#### GET /appointments
Foydalanuvchi uchrashuvlari

#### POST /appointments
Yangi uchrashuv belgilash

**Request:**
```json
{
    "doctor_id": "uuid",
    "session_id": "uuid",
    "scheduled_at": "2026-01-30T10:00:00Z",
    "notes": "Ko'rish o'tkirligi pasaygan"
}
```

#### GET /appointments/:id
Uchrashuv tafsilotlari

#### PATCH /appointments/:id
Uchrashuvni yangilash

#### DELETE /appointments/:id
Uchrashuvni bekor qilish

---

### ⚙️ Settings Endpoints (Public)

#### GET /settings/public
Ommaviy ilova sozlamalari

**Response:**
```json
{
    "success": true,
    "data": {
        "app_name": "EyeCare",
        "app_version": "1.0.0",
        "maintenance_mode": false,
        "supported_languages": ["uz", "ru", "en"],
        "test_distances": {
            "visualAcuity": 300,
            "colorBlindness": 75,
            ...
        },
        "enabled_tests": ["visualAcuity", "colorBlindness", ...]
    }
}
```

---

### 🔔 Notification Endpoints

#### GET /notifications
Foydalanuvchi bildirishnomalari

#### PATCH /notifications/:id/read
Bildirishnomani o'qilgan deb belgilash

#### POST /notifications/read-all
Barcha bildirishnomalarni o'qilgan deb belgilash

---

## 👨‍💼 Admin API Endpoints

### Base URL
```
/api/v1/admin
```

### 🔐 Admin Auth

#### POST /admin/auth/login
```json
{
    "username": "admin",
    "password": "securePassword",
    "two_factor_code": "123456"
}
```

### 📊 Dashboard

#### GET /admin/dashboard/stats
```json
{
    "success": true,
    "data": {
        "users": {
            "total": 15420,
            "new_today": 45,
            "new_this_week": 312,
            "active_today": 890
        },
        "tests": {
            "total_sessions": 45230,
            "completed_today": 156,
            "average_duration": 820,
            "completion_rate": 0.87
        },
        "appointments": {
            "total": 1250,
            "pending": 45,
            "today": 12
        },
        "revenue": {
            "total": 125000000,
            "this_month": 8500000
        }
    }
}
```

#### GET /admin/dashboard/charts
Grafiklar uchun ma'lumotlar

### 👥 User Management

#### GET /admin/users
#### GET /admin/users/:id
#### PATCH /admin/users/:id
#### DELETE /admin/users/:id
#### POST /admin/users/:id/block
#### POST /admin/users/:id/unblock

### 🧪 Test Management

#### GET /admin/tests/sessions
#### GET /admin/tests/sessions/:id
#### GET /admin/tests/analytics

### 👨‍⚕️ Doctor Management

#### GET /admin/doctors
#### POST /admin/doctors
#### GET /admin/doctors/:id
#### PATCH /admin/doctors/:id
#### DELETE /admin/doctors/:id
#### POST /admin/doctors/:id/verify

### ⚙️ Settings Management

#### GET /admin/settings
#### PATCH /admin/settings
#### GET /admin/settings/:key
#### PUT /admin/settings/:key

### 📊 Reports

#### GET /admin/reports/users
#### GET /admin/reports/tests
#### GET /admin/reports/revenue
#### POST /admin/reports/export

### 📝 Activity Logs

#### GET /admin/logs
Query: `action`, `actor_type`, `from_date`, `to_date`, `resource_type`

---

## 🤖 Telegram Bot Specification

### Bot Commands

| Command | Description | Handler |
|---------|-------------|---------|
| `/start` | Botni ishga tushirish | Welcome message + registration |
| `/help` | Yordam | Show all commands |
| `/test` | Test boshlash | Generate test link |
| `/results` | Natijalar | Show last 5 results |
| `/history` | Tarix | Full test history |
| `/doctors` | Shifokorlar | Nearest doctors list |
| `/appointment` | Uchrashuv | Book appointment |
| `/settings` | Sozlamalar | User settings |
| `/language` | Til | Change language |
| `/feedback` | Fikr-mulohaza | Send feedback |
| `/about` | Haqida | About the app |

### Bot States (FSM)

```
idle
├── registration
│   ├── awaiting_phone
│   ├── awaiting_code
│   └── awaiting_name
├── test
│   ├── confirming_start
│   └── awaiting_completion
├── appointment
│   ├── selecting_doctor
│   ├── selecting_date
│   └── confirming
├── feedback
│   └── awaiting_message
└── settings
    ├── changing_language
    └── changing_notifications
```

### Inline Keyboards

#### Main Menu
```
┌─────────────────────────────────┐
│  🔬 Testni Boshlash            │
├─────────────────────────────────┤
│  📊 Natijalarim  │  👨‍⚕️ Shifokorlar │
├─────────────────────────────────┤
│  📅 Uchrashuv    │  ⚙️ Sozlamalar  │
└─────────────────────────────────┘
```

### Webhook Events

#### Test Completed Notification
```json
{
    "type": "test_completed",
    "user_telegram_id": 123456789,
    "data": {
        "session_id": "uuid",
        "overall_status": "normal",
        "pdf_url": "https://..."
    }
}
```

#### Appointment Reminder
```json
{
    "type": "appointment_reminder",
    "user_telegram_id": 123456789,
    "data": {
        "appointment_id": "uuid",
        "doctor_name": "Dr. Abdullayev",
        "scheduled_at": "2026-01-30T10:00:00Z",
        "reminder_type": "24h" // or "1h"
    }
}
```

### Bot Message Templates

```javascript
const messages = {
    uz: {
        welcome: `🏥 *EyeCare* ko'z tekshiruvi botiga xush kelibsiz!\n\nBu bot orqali siz:\n• 🔬 10 ta professional ko'z testidan o'tishingiz\n• 📊 Natijalaringizni ko'rishingiz\n• 👨‍⚕️ Shifokor topishingiz mumkin`,
        
        test_start: `🔬 *Ko'z Tekshiruvini Boshlash*\n\nTest ~15 daqiqa davom etadi.\nYaxshi yoritilgan xonada bo'ling.\n\n👇 Boshlash uchun tugmani bosing:`,
        
        test_completed: `✅ *Test Yakunlandi!*\n\n📊 Umumiy holat: {status}\n⏱ Davomiyligi: {duration}\n\n📄 PDF hisobot: {pdf_url}`,
        
        reminder: `⏰ *Eslatma*\n\nSo'nggi ko'z tekshiruvidan {days} kun o'tdi.\n\nKo'z salomatligingiz uchun muntazam tekshiruv tavsiya etiladi.`
    },
    ru: { ... },
    en: { ... }
};
```

---

## 🔧 Background Jobs

### Job Queues

#### 1. PDF Generation Queue
```javascript
{
    name: 'generate-pdf',
    data: {
        session_id: 'uuid',
        user_id: 'uuid',
        template: 'detailed' // or 'summary'
    },
    options: {
        attempts: 3,
        backoff: { type: 'exponential', delay: 1000 },
        removeOnComplete: true
    }
}
```

#### 2. Notification Queue
```javascript
{
    name: 'send-notification',
    data: {
        user_id: 'uuid',
        type: 'reminder',
        channels: ['telegram', 'push'],
        template: 'test_reminder',
        variables: { days: 180 }
    }
}
```

#### 3. Reminder Scheduler (Cron)
```javascript
// Every day at 09:00 Tashkent time
{
    name: 'check-reminders',
    cron: '0 9 * * *',
    timezone: 'Asia/Tashkent'
}
```

#### 4. Cleanup Jobs
```javascript
// Clean expired sessions - every hour
{
    name: 'cleanup-expired-sessions',
    cron: '0 * * * *'
}

// Clean old activity logs - weekly
{
    name: 'cleanup-old-logs',
    cron: '0 3 * * 0', // Sunday 03:00
    data: { older_than_days: 90 }
}
```

---

## 🔒 Security Requirements

### Authentication
- JWT tokens with RS256 algorithm
- Access token: 1 hour expiry
- Refresh token: 30 days expiry, stored in HttpOnly cookie
- Token rotation on refresh

### Rate Limiting
```javascript
const rateLimits = {
    'auth/login': { max: 5, window: '15m' },
    'auth/register': { max: 3, window: '1h' },
    'auth/verify': { max: 10, window: '15m' },
    'tests/sessions': { max: 10, window: '1h' },
    'default': { max: 100, window: '15m' }
};
```

### Input Validation
- All inputs sanitized and validated with Zod/Joi
- SQL injection prevention via parameterized queries
- XSS prevention via content encoding

### CORS Configuration
```javascript
const corsOptions = {
    origin: [
        'https://eyecare.uz',
        'https://app.eyecare.uz',
        /\.eyecare\.uz$/
    ],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID']
};
```

### Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

---

## 📁 Project Structure

```
eyecare-backend/
├── src/
│   ├── app.js                 # Express app setup
│   ├── server.js              # Server entry point
│   │
│   ├── config/
│   │   ├── index.js           # Configuration loader
│   │   ├── database.js        # DB connection
│   │   ├── redis.js           # Redis connection
│   │   └── constants.js       # App constants
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── index.js       # Route aggregator
│   │   │   ├── auth.routes.js
│   │   │   ├── users.routes.js
│   │   │   ├── tests.routes.js
│   │   │   ├── results.routes.js
│   │   │   ├── doctors.routes.js
│   │   │   ├── appointments.routes.js
│   │   │   ├── notifications.routes.js
│   │   │   └── admin/
│   │   │       ├── index.js
│   │   │       ├── auth.routes.js
│   │   │       ├── users.routes.js
│   │   │       ├── doctors.routes.js
│   │   │       └── settings.routes.js
│   │   │
│   │   ├── controllers/
│   │   │   ├── auth.controller.js
│   │   │   ├── users.controller.js
│   │   │   ├── tests.controller.js
│   │   │   ├── results.controller.js
│   │   │   ├── doctors.controller.js
│   │   │   ├── appointments.controller.js
│   │   │   └── admin/
│   │   │       └── ...
│   │   │
│   │   ├── middlewares/
│   │   │   ├── auth.middleware.js
│   │   │   ├── admin.middleware.js
│   │   │   ├── rateLimiter.middleware.js
│   │   │   ├── validator.middleware.js
│   │   │   ├── errorHandler.middleware.js
│   │   │   └── requestLogger.middleware.js
│   │   │
│   │   └── validators/
│   │       ├── auth.validator.js
│   │       ├── users.validator.js
│   │       ├── tests.validator.js
│   │       └── ...
│   │
│   ├── services/
│   │   ├── auth.service.js
│   │   ├── users.service.js
│   │   ├── tests.service.js
│   │   ├── results.service.js
│   │   ├── doctors.service.js
│   │   ├── appointments.service.js
│   │   ├── notifications.service.js
│   │   ├── pdf.service.js
│   │   ├── sms.service.js
│   │   ├── email.service.js
│   │   └── storage.service.js
│   │
│   ├── models/
│   │   └── (Prisma models or equivalent)
│   │
│   ├── bot/
│   │   ├── index.js           # Bot initialization
│   │   ├── handlers/
│   │   │   ├── start.handler.js
│   │   │   ├── test.handler.js
│   │   │   ├── results.handler.js
│   │   │   ├── doctors.handler.js
│   │   │   └── settings.handler.js
│   │   ├── keyboards/
│   │   │   ├── main.keyboard.js
│   │   │   ├── inline.keyboard.js
│   │   │   └── ...
│   │   ├── middleware/
│   │   │   ├── auth.middleware.js
│   │   │   └── logger.middleware.js
│   │   └── locales/
│   │       ├── uz.js
│   │       ├── ru.js
│   │       └── en.js
│   │
│   ├── jobs/
│   │   ├── index.js           # Queue setup
│   │   ├── processors/
│   │   │   ├── pdf.processor.js
│   │   │   ├── notification.processor.js
│   │   │   └── cleanup.processor.js
│   │   └── schedulers/
│   │       ├── reminder.scheduler.js
│   │       └── cleanup.scheduler.js
│   │
│   ├── utils/
│   │   ├── logger.js
│   │   ├── response.js
│   │   ├── errors.js
│   │   ├── helpers.js
│   │   ├── crypto.js
│   │   └── date.js
│   │
│   └── templates/
│       ├── pdf/
│       │   └── report.html
│       └── email/
│           ├── verification.html
│           └── reminder.html
│
├── prisma/
│   ├── schema.prisma
│   ├── migrations/
│   └── seed.js
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
│
├── scripts/
│   ├── migrate.js
│   ├── seed.js
│   └── generate-docs.js
│
├── docs/
│   └── openapi.yaml
│
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json (if TypeScript)
└── README.md
```

---

## 🐳 Docker Configuration

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/eyecare
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  bot:
    build:
      context: .
      dockerfile: docker/Dockerfile.bot
    environment:
      - NODE_ENV=production
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=postgresql://user:pass@db:5432/eyecare
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/eyecare
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=eyecare
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    environment:
      - MINIO_ROOT_USER=minio
      - MINIO_ROOT_PASSWORD=minio123
    command: server /data --console-address ":9001"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

---

## 🌐 Environment Variables

```env
# App
NODE_ENV=development
PORT=3000
API_URL=http://localhost:3000
FRONTEND_URL=http://localhost:5173

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/eyecare

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_ACCESS_SECRET=your-access-secret-key-min-32-chars
JWT_REFRESH_SECRET=your-refresh-secret-key-min-32-chars
JWT_ACCESS_EXPIRY=1h
JWT_REFRESH_EXPIRY=30d

# Telegram Bot
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_WEBHOOK_URL=https://api.eyecare.uz/bot/webhook
BOT_WEBHOOK_SECRET=random-secret-string

# SMS (Eskiz.uz)
ESKIZ_EMAIL=your@email.com
ESKIZ_PASSWORD=your-password
ESKIZ_SENDER=EyeCare

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@eyecare.uz
SMTP_PASS=your-app-password
EMAIL_FROM="EyeCare <noreply@eyecare.uz>"

# Storage (MinIO/S3)
STORAGE_ENDPOINT=localhost
STORAGE_PORT=9000
STORAGE_ACCESS_KEY=minio
STORAGE_SECRET_KEY=minio123
STORAGE_BUCKET=eyecare
STORAGE_PUBLIC_URL=http://localhost:9000/eyecare

# Rate Limiting
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100

# Logging
LOG_LEVEL=debug
LOG_FORMAT=pretty

# Admin
ADMIN_DEFAULT_PASSWORD=eyecare2026
```

---

## 📝 API Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Noto'g'ri login yoki parol |
| `AUTH_TOKEN_EXPIRED` | 401 | Token muddati tugagan |
| `AUTH_TOKEN_INVALID` | 401 | Noto'g'ri token |
| `AUTH_UNAUTHORIZED` | 403 | Ruxsat yo'q |
| `AUTH_USER_BLOCKED` | 403 | Foydalanuvchi bloklangan |
| `VALIDATION_ERROR` | 400 | Validatsiya xatosi |
| `NOT_FOUND` | 404 | Resurs topilmadi |
| `CONFLICT` | 409 | Resurs allaqachon mavjud |
| `RATE_LIMIT_EXCEEDED` | 429 | So'rovlar limiti oshdi |
| `INTERNAL_ERROR` | 500 | Server xatosi |
| `SERVICE_UNAVAILABLE` | 503 | Xizmat vaqtincha mavjud emas |

---

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Seed data loaded (if needed)
- [ ] SSL certificates configured
- [ ] Domain DNS configured
- [ ] Firewall rules set

### Security
- [ ] Rate limiting enabled
- [ ] CORS configured for production domains
- [ ] Helmet middleware enabled
- [ ] SQL injection tests passed
- [ ] XSS tests passed
- [ ] Sensitive data encrypted

### Performance
- [ ] Database indexes created
- [ ] Redis caching enabled
- [ ] Gzip compression enabled
- [ ] Response time < 200ms

### Monitoring
- [ ] Health check endpoint working
- [ ] Error tracking configured (Sentry)
- [ ] Logging configured
- [ ] Uptime monitoring set up
- [ ] Alerts configured

---

## 📞 Support & Contact

**Developer:** EyeCare Team  
**Email:** dev@eyecare.uz  
**Telegram:** @eyecare_support

---

*Ushbu hujjat EyeCare backend tizimini to'liq yozish uchun mo'ljallangan. Barcha API endpointlar, ma'lumotlar bazasi sxemasi, xavfsizlik talablari va deployment yo'riqnomalarini o'z ichiga oladi.*

**Versiya:** 1.0.0  
**Yaratilgan:** 2026-01-24  
**Oxirgi yangilanish:** 2026-01-24
