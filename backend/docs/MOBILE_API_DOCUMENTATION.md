# 📱 EyeCare Mobile App - API Integration Documentation

## 🔗 API Base URL

```
Production: https://api.eyecare.uz/api/v1
Development: http://localhost:8000/api/v1
```

---

## 🔐 Authentication

### 1. Register User

**POST** `/auth/register`

```json
// Request
{
    "full_name": "Alisher Karimov",
    "phone_number": "+998901234567",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "birth_date": "1990-05-15",
    "gender": "male",
    "region": "Toshkent"
}

// Response (201 Created)
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "user": {
            "id": "uuid-string",
            "full_name": "Alisher Karimov",
            "phone_number": "+998901234567",
            "birth_date": "1990-05-15",
            "gender": "male",
            "region": "Toshkent",
            "created_at": "2024-01-15T10:30:00Z"
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
}
```

### 2. Login

**POST** `/auth/login`

```json
// Request
{
    "phone_number": "+998901234567",
    "password": "securepassword123"
}

// Response (200 OK)
{
    "success": true,
    "message": "Login successful",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

### 3. Refresh Token

**POST** `/auth/refresh`

```json
// Request
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

// Response (200 OK)
{
    "success": true,
    "data": {
        "access_token": "new-access-token...",
        "refresh_token": "new-refresh-token...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

### 4. SMS Verification

**POST** `/auth/send-sms`

```json
// Request
{
    "phone_number": "+998901234567"
}

// Response (200 OK)
{
    "success": true,
    "message": "SMS code sent successfully",
    "data": {
        "expires_in": 120
    }
}
```

**POST** `/auth/verify-sms`

```json
// Request
{
    "phone_number": "+998901234567",
    "code": "123456"
}

// Response (200 OK)
{
    "success": true,
    "message": "Phone verified successfully"
}
```

---

## 📱 Mobile Device Management

### 1. Register Device

**POST** `/mobile/device/register`

```json
// Request
{
    "device_id": "unique-device-uuid",
    "device_type": "android", // or "ios"
    "device_name": "Samsung Galaxy S21",
    "os_version": "Android 13",
    "app_version": "1.0.0",
    "push_token": "firebase-push-token-here"
}

// Response (200 OK)
{
    "success": true,
    "message": "Device registered successfully",
    "data": {
        "device_id": "unique-device-uuid",
        "registered_at": "2024-01-15T10:30:00Z"
    }
}
```

### 2. Update Push Token

**PUT** `/mobile/device/push-token`

```json
// Request
{
    "device_id": "unique-device-uuid",
    "push_token": "new-firebase-token"
}

// Response (200 OK)
{
    "success": true,
    "message": "Push token updated"
}
```

---

## 👤 User Profile

### 1. Get Profile

**GET** `/users/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "id": "uuid-string",
        "full_name": "Alisher Karimov",
        "phone_number": "+998901234567",
        "email": "alisher@example.com",
        "birth_date": "1990-05-15",
        "gender": "male",
        "region": "Toshkent",
        "avatar_url": "https://api.eyecare.uz/uploads/avatars/user123.jpg",
        "total_tests": 15,
        "last_test_date": "2024-01-14T15:00:00Z",
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

### 2. Update Profile

**PUT** `/users/me`

```json
// Request
{
    "full_name": "Alisher Karimov",
    "email": "newemail@example.com",
    "birth_date": "1990-05-15",
    "region": "Samarqand"
}

// Response (200 OK)
{
    "success": true,
    "message": "Profile updated successfully",
    "data": { /* updated user object */ }
}
```

### 3. Upload Avatar

**POST** `/mobile/profile/avatar`

**Content-Type:** `multipart/form-data`

```
file: [binary image data]
```

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "avatar_url": "https://api.eyecare.uz/uploads/avatars/user123.jpg"
    }
}
```

---

## 🧪 Eye Tests

### 1. Get Available Test Types

**GET** `/mobile/tests/types`

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "test_types": [
            {
                "id": "visual_acuity",
                "name": "Ko'rish o'tkirligi",
                "name_en": "Visual Acuity",
                "description": "Snellen chart yordamida ko'rish o'tkirligini aniqlash",
                "duration_minutes": 5,
                "icon": "eye",
                "distance_meters": 5,
                "requires_both_eyes": true,
                "instructions": [
                    "5 metr masofada turing",
                    "Avval o'ng ko'zni tekshiring",
                    "Keyin chap ko'zni tekshiring"
                ]
            },
            {
                "id": "color_blindness",
                "name": "Rang ko'rish",
                "name_en": "Color Blindness",
                "description": "Ishihara plitalari bilan rang ko'rishni tekshirish",
                "duration_minutes": 3,
                "icon": "palette",
                "distance_meters": 0.5,
                "requires_both_eyes": false
            },
            {
                "id": "contrast_sensitivity",
                "name": "Kontrast sezgirligi",
                "name_en": "Contrast Sensitivity",
                "description": "Turli kontrastlarda ko'rish qobiliyatini tekshirish",
                "duration_minutes": 4,
                "icon": "contrast"
            },
            {
                "id": "astigmatism",
                "name": "Astigmatizm",
                "name_en": "Astigmatism",
                "description": "Astigmatizmni aniqlash",
                "duration_minutes": 3,
                "icon": "astigmatism"
            },
            {
                "id": "amsler_grid",
                "name": "Amsler panjarasi",
                "name_en": "Amsler Grid",
                "description": "Makula degeneratsiyasini aniqlash",
                "duration_minutes": 2,
                "icon": "grid"
            },
            {
                "id": "near_vision",
                "name": "Yaqin ko'rish",
                "name_en": "Near Vision",
                "description": "Yaqin masofadan o'qish qobiliyatini tekshirish",
                "duration_minutes": 3,
                "icon": "book"
            },
            {
                "id": "dry_eye",
                "name": "Quruq ko'z",
                "name_en": "Dry Eye Test",
                "description": "Ko'z quruqligi simptomlarini baholash",
                "duration_minutes": 2,
                "icon": "drop"
            },
            {
                "id": "eye_fatigue",
                "name": "Ko'z charchoqi",
                "name_en": "Eye Fatigue",
                "description": "Ko'z charchoq darajasini aniqlash",
                "duration_minutes": 3,
                "icon": "tired"
            },
            {
                "id": "light_sensitivity",
                "name": "Yorug'lik sezgirligi",
                "name_en": "Light Sensitivity",
                "description": "Fotofobiyani tekshirish",
                "duration_minutes": 2,
                "icon": "sun"
            },
            {
                "id": "peripheral_vision",
                "name": "Periferik ko'rish",
                "name_en": "Peripheral Vision",
                "description": "Yon ko'rish maydonini tekshirish",
                "duration_minutes": 5,
                "icon": "expand"
            }
        ]
    }
}
```

### 2. Start Test Session

**POST** `/mobile/tests/start`

```json
// Request
{
    "test_type": "visual_acuity",
    "device_info": {
        "screen_width": 1080,
        "screen_height": 2400,
        "screen_dpi": 420,
        "brightness": 80
    }
}

// Response (200 OK)
{
    "success": true,
    "data": {
        "session_id": "test-session-uuid",
        "test_type": "visual_acuity",
        "started_at": "2024-01-15T10:30:00Z",
        "calibration_data": {
            "letter_size_mm": 8.73,
            "recommended_distance_cm": 500,
            "pixel_per_mm": 16.5
        }
    }
}
```

### 3. Submit Test Result

**POST** `/mobile/tests/{session_id}/result`

```json
// Request
{
    "eye": "right", // "right", "left", or "both"
    "result_data": {
        "visual_acuity": "6/6",
        "smallest_line_read": 8,
        "errors": 2,
        "time_seconds": 45
    },
    "answers": [
        {"optotype": "E", "direction": "right", "correct": true},
        {"optotype": "F", "direction": "up", "correct": true},
        {"optotype": "P", "direction": "left", "correct": false}
    ]
}

// Response (200 OK)
{
    "success": true,
    "data": {
        "session_id": "test-session-uuid",
        "eye": "right",
        "score": 85,
        "interpretation": "Yaxshi ko'rish",
        "saved": true
    }
}
```

### 4. Complete Test Session

**POST** `/mobile/tests/{session_id}/complete`

```json
// Request
{
    "notes": "Yoritish yaxshi edi"
}

// Response (200 OK)
{
    "success": true,
    "data": {
        "session_id": "test-session-uuid",
        "completed_at": "2024-01-15T10:35:00Z",
        "duration_seconds": 300,
        "overall_result": {
            "right_eye": {
                "visual_acuity": "6/6",
                "score": 85,
                "status": "normal"
            },
            "left_eye": {
                "visual_acuity": "6/9",
                "score": 70,
                "status": "mild_impairment"
            }
        },
        "recommendations": [
            "Chap ko'zni kuzatib borish tavsiya etiladi",
            "6 oydan keyin qayta tekshiruvdan o'ting"
        ],
        "should_see_doctor": false
    }
}
```

### 5. Get Test History

**GET** `/tests/history`

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `test_type` (string): Filter by test type
- `date_from` (string): Filter from date (YYYY-MM-DD)
- `date_to` (string): Filter to date (YYYY-MM-DD)

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "test-uuid",
                "test_type": "visual_acuity",
                "test_name": "Ko'rish o'tkirligi",
                "date": "2024-01-15T10:30:00Z",
                "right_eye_result": {
                    "visual_acuity": "6/6",
                    "score": 85
                },
                "left_eye_result": {
                    "visual_acuity": "6/9",
                    "score": 70
                },
                "overall_status": "normal"
            }
        ],
        "total": 15,
        "page": 1,
        "limit": 20,
        "pages": 1
    }
}
```

### 6. Get Single Test Result

**GET** `/tests/{test_id}`

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "id": "test-uuid",
        "test_type": "visual_acuity",
        "test_name": "Ko'rish o'tkirligi",
        "date": "2024-01-15T10:30:00Z",
        "duration_seconds": 300,
        "right_eye_result": {
            "visual_acuity": "6/6",
            "score": 85,
            "details": {
                "smallest_line": 8,
                "errors": 2
            }
        },
        "left_eye_result": {
            "visual_acuity": "6/9",
            "score": 70,
            "details": {
                "smallest_line": 6,
                "errors": 3
            }
        },
        "recommendations": [
            "Chap ko'zni kuzatib borish tavsiya etiladi"
        ],
        "device_info": {
            "device_name": "Samsung Galaxy S21",
            "screen_brightness": 80
        }
    }
}
```

### 7. Generate PDF Report

**GET** `/tests/{test_id}/pdf`

```
// Response: application/pdf binary data
// Content-Disposition: attachment; filename="eyecare_report_20240115.pdf"
```

---

## 👨‍⚕️ Doctors

### 1. Get Doctors List

**GET** `/mobile/doctors`

**Query Parameters:**
- `region` (string): Filter by region
- `specialization` (string): Filter by specialization
- `rating_min` (float): Minimum rating (1-5)
- `available_only` (bool): Only show available doctors
- `page` (int): Page number
- `limit` (int): Items per page

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "doctor-uuid",
                "full_name": "Dr. Anvar Toshmatov",
                "specialization": "Oftalmolog",
                "clinic_name": "Ko'z Salomatligi Markazi",
                "clinic_address": "Toshkent sh., Yunusobod t., Amir Temur ko'chasi 15",
                "phone_number": "+998712345678",
                "rating": 4.8,
                "reviews_count": 156,
                "experience_years": 15,
                "photo_url": "https://api.eyecare.uz/uploads/doctors/dr_anvar.jpg",
                "is_available": true,
                "next_available_slot": "2024-01-16T09:00:00Z",
                "consultation_price": 150000,
                "location": {
                    "lat": 41.311151,
                    "lng": 69.279737
                }
            }
        ],
        "total": 45,
        "page": 1,
        "limit": 20
    }
}
```

### 2. Get Doctor Details

**GET** `/doctors/{doctor_id}`

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "id": "doctor-uuid",
        "full_name": "Dr. Anvar Toshmatov",
        "specialization": "Oftalmolog",
        "bio": "15 yillik tajribaga ega ko'z shifokori...",
        "education": [
            "Toshkent Tibbiyot Akademiyasi (2005-2011)",
            "Oftalmologiya bo'yicha rezidentura (2011-2013)"
        ],
        "certifications": [
            "Oftalmolog mutaxassisligi sertifikati",
            "Lazer ko'rish tuzatish sertifikati"
        ],
        "clinic_name": "Ko'z Salomatligi Markazi",
        "clinic_address": "Toshkent sh., Yunusobod t., Amir Temur ko'chasi 15",
        "phone_number": "+998712345678",
        "email": "dr.anvar@eyeclinic.uz",
        "rating": 4.8,
        "reviews_count": 156,
        "experience_years": 15,
        "photo_url": "https://api.eyecare.uz/uploads/doctors/dr_anvar.jpg",
        "gallery": [
            "https://api.eyecare.uz/uploads/clinics/clinic1_1.jpg",
            "https://api.eyecare.uz/uploads/clinics/clinic1_2.jpg"
        ],
        "services": [
            {"name": "Ko'rik", "price": 150000},
            {"name": "Ko'z tubi tekshiruvi", "price": 200000},
            {"name": "Lazer tuzatish konsultatsiyasi", "price": 100000}
        ],
        "working_hours": {
            "monday": {"from": "09:00", "to": "18:00"},
            "tuesday": {"from": "09:00", "to": "18:00"},
            "wednesday": {"from": "09:00", "to": "18:00"},
            "thursday": {"from": "09:00", "to": "18:00"},
            "friday": {"from": "09:00", "to": "17:00"},
            "saturday": {"from": "10:00", "to": "14:00"},
            "sunday": null
        },
        "location": {
            "lat": 41.311151,
            "lng": 69.279737
        }
    }
}
```

### 3. Get Doctor Available Slots

**GET** `/doctors/{doctor_id}/slots`

**Query Parameters:**
- `date` (string): Date to check (YYYY-MM-DD)

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "date": "2024-01-16",
        "doctor_id": "doctor-uuid",
        "slots": [
            {"time": "09:00", "available": true},
            {"time": "09:30", "available": true},
            {"time": "10:00", "available": false},
            {"time": "10:30", "available": true},
            {"time": "11:00", "available": true},
            {"time": "11:30", "available": false},
            {"time": "14:00", "available": true},
            {"time": "14:30", "available": true},
            {"time": "15:00", "available": true}
        ]
    }
}
```

---

## 📅 Appointments

### 1. Book Appointment

**POST** `/mobile/appointments`

```json
// Request
{
    "doctor_id": "doctor-uuid",
    "date": "2024-01-16",
    "time": "09:00",
    "reason": "Ko'rish tekshiruvi",
    "notes": "So'nggi testlar natijalarini ko'rsatmoqchiman",
    "attach_test_ids": ["test-uuid-1", "test-uuid-2"]
}

// Response (201 Created)
{
    "success": true,
    "message": "Appointment booked successfully",
    "data": {
        "id": "appointment-uuid",
        "doctor": {
            "id": "doctor-uuid",
            "full_name": "Dr. Anvar Toshmatov",
            "clinic_name": "Ko'z Salomatligi Markazi",
            "clinic_address": "Toshkent sh., Yunusobod t., Amir Temur ko'chasi 15"
        },
        "date": "2024-01-16",
        "time": "09:00",
        "status": "confirmed",
        "confirmation_code": "EYE-2024-1234"
    }
}
```

### 2. Get My Appointments

**GET** `/users/me/appointments`

**Query Parameters:**
- `status` (string): Filter by status (upcoming, completed, cancelled)
- `page` (int): Page number
- `limit` (int): Items per page

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "appointment-uuid",
                "doctor": {
                    "id": "doctor-uuid",
                    "full_name": "Dr. Anvar Toshmatov",
                    "specialization": "Oftalmolog",
                    "photo_url": "https://api.eyecare.uz/uploads/doctors/dr_anvar.jpg"
                },
                "clinic_name": "Ko'z Salomatligi Markazi",
                "clinic_address": "Toshkent sh., Yunusobod t., Amir Temur ko'chasi 15",
                "date": "2024-01-16",
                "time": "09:00",
                "status": "confirmed",
                "confirmation_code": "EYE-2024-1234",
                "created_at": "2024-01-15T10:30:00Z"
            }
        ],
        "total": 3,
        "page": 1,
        "limit": 20
    }
}
```

### 3. Cancel Appointment

**DELETE** `/users/me/appointments/{appointment_id}`

```json
// Request
{
    "reason": "Vaqtim o'zgardi"
}

// Response (200 OK)
{
    "success": true,
    "message": "Appointment cancelled successfully"
}
```

---

## 🔄 Offline Sync

### 1. Sync Offline Data

**POST** `/mobile/sync`

```json
// Request
{
    "last_sync_at": "2024-01-14T10:00:00Z",
    "pending_tests": [
        {
            "local_id": "local-test-1",
            "test_type": "visual_acuity",
            "completed_at": "2024-01-15T08:00:00Z",
            "results": {
                "right_eye": {"visual_acuity": "6/6", "score": 85},
                "left_eye": {"visual_acuity": "6/9", "score": 70}
            }
        }
    ],
    "pending_answers": []
}

// Response (200 OK)
{
    "success": true,
    "data": {
        "synced_at": "2024-01-15T11:00:00Z",
        "uploaded_tests": [
            {
                "local_id": "local-test-1",
                "server_id": "test-uuid-from-server"
            }
        ],
        "new_data": {
            "notifications": [
                {
                    "id": "notif-1",
                    "type": "reminder",
                    "title": "Test eslatmasi",
                    "message": "Haftalik ko'z tekshiruvini o'tkazing",
                    "created_at": "2024-01-15T09:00:00Z"
                }
            ],
            "updated_doctors": [],
            "app_settings": {
                "min_app_version": "1.0.0",
                "force_update": false
            }
        }
    }
}
```

---

## 🔔 Notifications

### 1. Get Notifications

**GET** `/users/me/notifications`

**Query Parameters:**
- `unread_only` (bool): Only unread notifications
- `page` (int): Page number
- `limit` (int): Items per page

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "notif-uuid",
                "type": "appointment_reminder",
                "title": "Uchrashuv eslatmasi",
                "message": "Ertaga soat 09:00 da Dr. Anvar bilan uchrashuvingiz bor",
                "read": false,
                "data": {
                    "appointment_id": "appointment-uuid"
                },
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "notif-uuid-2",
                "type": "test_reminder",
                "title": "Tekshiruv vaqti!",
                "message": "Haftalik ko'z tekshiruvini o'tkazish vaqti keldi",
                "read": true,
                "created_at": "2024-01-14T09:00:00Z"
            }
        ],
        "unread_count": 5,
        "total": 23,
        "page": 1,
        "limit": 20
    }
}
```

### 2. Mark Notification as Read

**PUT** `/users/me/notifications/{notification_id}/read`

```json
// Response (200 OK)
{
    "success": true,
    "message": "Notification marked as read"
}
```

### 3. Mark All as Read

**PUT** `/users/me/notifications/read-all`

```json
// Response (200 OK)
{
    "success": true,
    "message": "All notifications marked as read"
}
```

---

## 📊 Statistics & Dashboard

### 1. Get User Dashboard

**GET** `/mobile/dashboard`

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "user_summary": {
            "total_tests": 45,
            "tests_this_month": 8,
            "last_test_date": "2024-01-15T10:30:00Z",
            "streak_days": 7,
            "health_score": 85
        },
        "recent_results": {
            "visual_acuity": {
                "current": "6/6",
                "trend": "stable",
                "last_change": null
            },
            "color_vision": {
                "current": "Normal",
                "trend": "stable"
            }
        },
        "recommendations": [
            {
                "type": "test_reminder",
                "message": "Ko'rish o'tkirligi testini o'tkazing",
                "priority": "medium"
            }
        ],
        "upcoming_appointments": [
            {
                "id": "appointment-uuid",
                "doctor_name": "Dr. Anvar Toshmatov",
                "date": "2024-01-16",
                "time": "09:00"
            }
        ],
        "health_tips": [
            "Har 20 daqiqada 20 soniya davomida 20 fut (6m) masofaga qarang",
            "Kuniga kamida 2 litr suv iching"
        ]
    }
}
```

### 2. Get Test Statistics

**GET** `/tests/statistics`

**Query Parameters:**
- `period` (string): week, month, year, all

```json
// Response (200 OK)
{
    "success": true,
    "data": {
        "period": "month",
        "total_tests": 25,
        "by_type": {
            "visual_acuity": 8,
            "color_blindness": 4,
            "contrast_sensitivity": 5,
            "astigmatism": 4,
            "amsler_grid": 4
        },
        "trends": {
            "visual_acuity": {
                "values": [
                    {"date": "2024-01-01", "right": 85, "left": 70},
                    {"date": "2024-01-08", "right": 85, "left": 72},
                    {"date": "2024-01-15", "right": 87, "left": 75}
                ],
                "trend": "improving"
            }
        },
        "average_scores": {
            "visual_acuity": 82,
            "color_blindness": 95,
            "contrast_sensitivity": 78
        }
    }
}
```

---

## ⚠️ Error Responses

All error responses follow this format:

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Validation failed",
        "details": [
            {
                "field": "phone_number",
                "message": "Invalid phone number format"
            }
        ]
    }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `DUPLICATE_ENTRY` | 409 | Resource already exists |
| `TOKEN_EXPIRED` | 401 | JWT token expired |
| `INVALID_CREDENTIALS` | 401 | Wrong phone/password |

---

## 📱 Mobile Integration Code Examples

### Kotlin (Android)

```kotlin
// Retrofit Interface
interface EyeCareApi {
    
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>
    
    @GET("mobile/tests/types")
    suspend fun getTestTypes(): Response<TestTypesResponse>
    
    @POST("mobile/tests/start")
    suspend fun startTest(@Body request: StartTestRequest): Response<TestSessionResponse>
    
    @POST("mobile/tests/{sessionId}/result")
    suspend fun submitResult(
        @Path("sessionId") sessionId: String,
        @Body result: TestResultRequest
    ): Response<ResultResponse>
    
    @GET("mobile/doctors")
    suspend fun getDoctors(
        @Query("region") region: String? = null,
        @Query("page") page: Int = 1
    ): Response<DoctorsResponse>
}

// Data Classes
data class LoginRequest(
    val phone_number: String,
    val password: String
)

data class AuthResponse(
    val success: Boolean,
    val data: AuthData?
)

data class AuthData(
    val access_token: String,
    val refresh_token: String,
    val token_type: String
)

// Repository
class EyeCareRepository(private val api: EyeCareApi) {
    
    suspend fun login(phone: String, password: String): Result<AuthData> {
        return try {
            val response = api.login(LoginRequest(phone, password))
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!)
            } else {
                Result.failure(Exception("Login failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Swift (iOS)

```swift
// API Client
class EyeCareAPI {
    static let shared = EyeCareAPI()
    private let baseURL = "https://api.eyecare.uz/api/v1"
    
    func login(phone: String, password: String) async throws -> AuthResponse {
        let url = URL(string: "\(baseURL)/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["phone_number": phone, "password": password]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(AuthResponse.self, from: data)
    }
    
    func getTestTypes() async throws -> TestTypesResponse {
        let url = URL(string: "\(baseURL)/mobile/tests/types")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(TokenManager.accessToken)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(TestTypesResponse.self, from: data)
    }
    
    func startTest(testType: String, deviceInfo: DeviceInfo) async throws -> TestSession {
        let url = URL(string: "\(baseURL)/mobile/tests/start")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(TokenManager.accessToken)", forHTTPHeaderField: "Authorization")
        
        let body = StartTestRequest(test_type: testType, device_info: deviceInfo)
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(TestSessionResponse.self, from: data).data
    }
}

// Models
struct AuthResponse: Codable {
    let success: Bool
    let data: AuthData?
}

struct AuthData: Codable {
    let access_token: String
    let refresh_token: String
    let token_type: String
}

struct TestSession: Codable {
    let session_id: String
    let test_type: String
    let started_at: Date
    let calibration_data: CalibrationData?
}
```

### React Native / Flutter

```typescript
// React Native - API Service
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE = 'https://api.eyecare.uz/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API Functions
export const authApi = {
  login: (phone: string, password: string) =>
    api.post('/auth/login', { phone_number: phone, password }),
  
  register: (data: RegisterData) =>
    api.post('/auth/register', data),
  
  refreshToken: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
};

export const testApi = {
  getTestTypes: () => api.get('/mobile/tests/types'),
  
  startTest: (testType: string, deviceInfo: DeviceInfo) =>
    api.post('/mobile/tests/start', { test_type: testType, device_info: deviceInfo }),
  
  submitResult: (sessionId: string, result: TestResult) =>
    api.post(`/mobile/tests/${sessionId}/result`, result),
  
  completeTest: (sessionId: string) =>
    api.post(`/mobile/tests/${sessionId}/complete`),
  
  getHistory: (params?: { page?: number; test_type?: string }) =>
    api.get('/tests/history', { params }),
};

export const doctorApi = {
  getDoctors: (params?: DoctorFilterParams) =>
    api.get('/mobile/doctors', { params }),
  
  getDoctorDetails: (doctorId: string) =>
    api.get(`/doctors/${doctorId}`),
  
  getSlots: (doctorId: string, date: string) =>
    api.get(`/doctors/${doctorId}/slots`, { params: { date } }),
  
  bookAppointment: (data: AppointmentData) =>
    api.post('/mobile/appointments', data),
};

export const syncApi = {
  syncData: (data: SyncRequest) =>
    api.post('/mobile/sync', data),
};
```

---

## 🔒 Security Headers

All requests should include:

```
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
X-Device-ID: {unique_device_id}
X-App-Version: 1.0.0
X-Platform: android|ios
```

---

## 📋 Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/auth/*` | 10 requests/minute |
| `/mobile/tests/*` | 30 requests/minute |
| `/mobile/sync` | 5 requests/minute |
| Other endpoints | 60 requests/minute |

---

## 🧪 Test Credentials (Development Only)

```
Phone: +998900000000
Password: test123456
```

---

## 📞 Support

- Email: support@eyecare.uz
- Telegram: @eyecare_support
- API Status: https://status.eyecare.uz
