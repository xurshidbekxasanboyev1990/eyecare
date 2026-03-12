"""
EyeCare Bot - Telegram Inline Keyboards

Barcha Telegram bot klaviaturalari
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from typing import Optional


class Keyboards:
    """Telegram bot uchun barcha klaviaturalar"""
    
    # ==================== MAIN MENU ====================
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Asosiy menyu"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🩺 Ko'z tekshiruvi", callback_data="start_screening"),
                InlineKeyboardButton(text="👁️ Testlar", callback_data="tests_menu")
            ],
            [
                InlineKeyboardButton(text="👨‍⚕️ Shifokorlar", callback_data="doctors_list"),
                InlineKeyboardButton(text="📋 Tarix", callback_data="my_history")
            ],
            [
                InlineKeyboardButton(text="ℹ️ Ma'lumot", callback_data="info"),
                InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")
            ]
        ])
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Asosiy menyuga qaytish"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
        ])
    
    # ==================== GENDER SELECTION ====================
    
    @staticmethod
    def gender_selection() -> InlineKeyboardMarkup:
        """Jinsni tanlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Erkak", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 Ayol", callback_data="gender_female")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")
            ]
        ])
    
    # ==================== YES/NO QUESTIONS ====================
    
    @staticmethod
    def yes_no(callback_prefix: str, show_back: bool = True) -> InlineKeyboardMarkup:
        """Ha/Yo'q tugmalari"""
        buttons = [
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=f"{callback_prefix}_yes"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=f"{callback_prefix}_no")
            ]
        ]
        if show_back:
            buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def eye_fatigue() -> InlineKeyboardMarkup:
        """Ko'z charchashi savoli"""
        return Keyboards.yes_no("eye_fatigue")
    
    @staticmethod
    def cataract_symptoms() -> InlineKeyboardMarkup:
        """Katarakta simptomlari"""
        return Keyboards.yes_no("cataract")
    
    @staticmethod
    def myopia_symptoms() -> InlineKeyboardMarkup:
        """Miopiya simptomlari"""
        return Keyboards.yes_no("myopia")
    
    @staticmethod
    def glaucoma_symptoms() -> InlineKeyboardMarkup:
        """Glaukoma simptomlari"""
        return Keyboards.yes_no("glaucoma")
    
    @staticmethod
    def chorioretinitis_symptoms() -> InlineKeyboardMarkup:
        """Xorioretinit simptomlari"""
        return Keyboards.yes_no("chorioretinitis")
    
    @staticmethod
    def retinal_dystrophy_symptoms() -> InlineKeyboardMarkup:
        """To'r parda distrofiyasi simptomlari"""
        return Keyboards.yes_no("retinal_dystrophy")
    
    # ==================== EYE SELECTION ====================
    
    @staticmethod
    def eye_selection() -> InlineKeyboardMarkup:
        """Ko'zni tanlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👁️ O'ng ko'z", callback_data="eye_right"),
                InlineKeyboardButton(text="👁️ Chap ko'z", callback_data="eye_left")
            ],
            [
                InlineKeyboardButton(text="👁️‍🗨️ Ikkala ko'z", callback_data="eye_both")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    # ==================== TESTS MENU ====================
    
    @staticmethod
    def tests_menu() -> InlineKeyboardMarkup:
        """Testlar menyusi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Ko'rish keskinligi", callback_data="test_visual_acuity")
            ],
            [
                InlineKeyboardButton(text="🎨 Rang ajratish", callback_data="test_color_blindness")
            ],
            [
                InlineKeyboardButton(text="📐 Astigmatizm", callback_data="test_astigmatism")
            ],
            [
                InlineKeyboardButton(text="🔲 Amsler grid", callback_data="test_amsler")
            ],
            [
                InlineKeyboardButton(text="🌓 Kontrast sezgirlik", callback_data="test_contrast")
            ],
            [
                InlineKeyboardButton(text="📏 Yaqindan ko'rish", callback_data="test_near_vision")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")
            ]
        ])
    
    @staticmethod
    def all_tests_menu() -> InlineKeyboardMarkup:
        """Barcha testlar ro'yxati"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👁️ Ko'rish keskinligi", callback_data="test_snellen")
            ],
            [
                InlineKeyboardButton(text="🌈 Ishihara", callback_data="test_ishihara")
            ],
            [
                InlineKeyboardButton(text="📐 Astigmatizm testi", callback_data="test_astigmatism")
            ],
            [
                InlineKeyboardButton(text="🔲 Amsler Grid", callback_data="test_amsler")
            ],
            [
                InlineKeyboardButton(text="◐ Kontrast testi", callback_data="test_contrast")
            ],
            [
                InlineKeyboardButton(text="📖 Yaqin ko'rish", callback_data="test_reading")
            ],
            [
                InlineKeyboardButton(text="🌑 Qorong'i adaptatsiya", callback_data="test_dark_adaptation")
            ],
            [
                InlineKeyboardButton(text="👀 Periferik ko'rish", callback_data="test_peripheral")
            ],
            [
                InlineKeyboardButton(text="🏃 Harakat aniqlash", callback_data="test_motion")
            ],
            [
                InlineKeyboardButton(text="📏 Chuqurlik qabul qilish", callback_data="test_depth")
            ],
            [
                InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="main_menu")
            ]
        ])
    
    # ==================== WEB APP LAUNCHERS ====================
    
    @staticmethod
    def start_test_webapp(webapp_url: str, test_type: str, test_name: str) -> InlineKeyboardMarkup:
        """Test boshlash uchun WebApp tugmasi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🚀 {test_name} testini boshlash",
                    web_app=WebAppInfo(url=f"{webapp_url}/test/{test_type}")
                )
            ],
            [
                InlineKeyboardButton(text="ℹ️ Ko'rsatma", callback_data=f"instruction_{test_type}"),
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="tests_menu")
            ]
        ])
    
    @staticmethod
    def webapp_button(webapp_url: str, text: str = "🔬 Testni boshlash") -> InlineKeyboardMarkup:
        """Umumiy WebApp tugmasi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    web_app=WebAppInfo(url=webapp_url)
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    @staticmethod
    def full_webapp(webapp_url: str) -> InlineKeyboardMarkup:
        """To'liq ilovani ochish"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Ilovani ochish",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ])
    
    # ==================== TEST INSTRUCTIONS ====================
    
    @staticmethod
    def test_ready(test_type: str, webapp_url: str) -> InlineKeyboardMarkup:
        """Test uchun tayyor - ko'rsatma o'qilgandan keyin"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tayorman, boshlash",
                    web_app=WebAppInfo(url=f"{webapp_url}/test/{test_type}")
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="tests_menu")
            ]
        ])
    
    # ==================== SCREENING FLOW ====================
    
    @staticmethod
    def continue_screening() -> InlineKeyboardMarkup:
        """Skriningni davom ettirish"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➡️ Davom etish", callback_data="continue_screening")
            ],
            [
                InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
            ]
        ])
    
    @staticmethod
    def screening_complete() -> InlineKeyboardMarkup:
        """Skrining tugadi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Natijalarni ko'rish", callback_data="view_results")
            ],
            [
                InlineKeyboardButton(text="👨‍⚕️ Shifokorga yozilish", callback_data="book_appointment")
            ],
            [
                InlineKeyboardButton(text="🔄 Qayta tekshirish", callback_data="start_screening")
            ],
            [
                InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
            ]
        ])
    
    @staticmethod
    def after_diagnosis() -> InlineKeyboardMarkup:
        """Tashxisdan keyin"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💊 Dorilar haqida", callback_data="medicine_info")
            ],
            [
                InlineKeyboardButton(text="👨‍⚕️ Shifokor bilan bog'lanish", callback_data="contact_doctor")
            ],
            [
                InlineKeyboardButton(text="📥 PDF yuklab olish", callback_data="download_pdf")
            ],
            [
                InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
            ]
        ])
    
    # ==================== DOCTORS ====================
    
    @staticmethod
    def doctors_list(doctors: list, page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """Shifokorlar ro'yxati"""
        buttons = []
        
        for doctor in doctors:
            rating = "⭐" * int(doctor.get("rating", 0))
            buttons.append([
                InlineKeyboardButton(
                    text=f"👨‍⚕️ {doctor['name']} {rating}",
                    callback_data=f"doctor_{doctor['id']}"
                )
            ])
        
        # Pagination
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"doctors_page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"doctors_page_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def doctor_profile(doctor_id: int) -> InlineKeyboardMarkup:
        """Shifokor profili"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Uchrashuv belgilash", callback_data=f"book_doctor_{doctor_id}")
            ],
            [
                InlineKeyboardButton(text="📞 Qo'ng'iroq qilish", callback_data=f"call_doctor_{doctor_id}"),
                InlineKeyboardButton(text="💬 Yozish", callback_data=f"message_doctor_{doctor_id}")
            ],
            [
                InlineKeyboardButton(text="⭐ Baho berish", callback_data=f"rate_doctor_{doctor_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="doctors_list")
            ]
        ])
    
    @staticmethod
    def appointment_times(doctor_id: int, times: list) -> InlineKeyboardMarkup:
        """Uchrashuv vaqtlari"""
        buttons = []
        row = []
        
        for i, time_slot in enumerate(times):
            row.append(InlineKeyboardButton(
                text=time_slot["display"],
                callback_data=f"time_{doctor_id}_{time_slot['id']}"
            ))
            if (i + 1) % 3 == 0:
                buttons.append(row)
                row = []
        
        if row:
            buttons.append(row)
        
        buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"doctor_{doctor_id}")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def confirm_appointment(doctor_id: int, time_id: str) -> InlineKeyboardMarkup:
        """Uchrashuvni tasdiqlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_{doctor_id}_{time_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"doctor_{doctor_id}")
            ]
        ])
    
    # ==================== RATING ====================
    
    @staticmethod
    def rating_stars(callback_prefix: str) -> InlineKeyboardMarkup:
        """Baho yulduzlari"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐", callback_data=f"{callback_prefix}_1"),
                InlineKeyboardButton(text="⭐⭐", callback_data=f"{callback_prefix}_2"),
                InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"{callback_prefix}_3"),
                InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"{callback_prefix}_4"),
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"{callback_prefix}_5")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    # ==================== HISTORY ====================
    
    @staticmethod
    def history_menu() -> InlineKeyboardMarkup:
        """Tarix menyusi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🩺 Skrining tarixi", callback_data="screening_history")
            ],
            [
                InlineKeyboardButton(text="📊 Test natijalari", callback_data="test_history")
            ],
            [
                InlineKeyboardButton(text="📅 Uchrashuvlar", callback_data="appointment_history")
            ],
            [
                InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="main_menu")
            ]
        ])
    
    @staticmethod
    def history_item(item_id: int, item_type: str) -> InlineKeyboardMarkup:
        """Tarix elementi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📥 PDF yuklab olish", callback_data=f"download_{item_type}_{item_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"{item_type}_history")
            ]
        ])
    
    # ==================== SETTINGS ====================
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Sozlamalar menyusi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌐 Til", callback_data="settings_language"),
                InlineKeyboardButton(text="🔔 Bildirishnomalar", callback_data="settings_notifications")
            ],
            [
                InlineKeyboardButton(text="👤 Profil", callback_data="settings_profile")
            ],
            [
                InlineKeyboardButton(text="📱 Ilovani o'rnatish", callback_data="install_app")
            ],
            [
                InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="main_menu")
            ]
        ])
    
    @staticmethod
    def language_selection() -> InlineKeyboardMarkup:
        """Til tanlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
            ],
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings")
            ]
        ])
    
    @staticmethod
    def notifications_settings(notifications_enabled: bool) -> InlineKeyboardMarkup:
        """Bildirishnoma sozlamalari"""
        status = "✅ Yoqilgan" if notifications_enabled else "❌ O'chirilgan"
        action = "disable" if notifications_enabled else "enable"
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=status, callback_data=f"notifications_{action}")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings")
            ]
        ])
    
    # ==================== INFO ====================
    
    @staticmethod
    def info_menu() -> InlineKeyboardMarkup:
        """Ma'lumot menyusi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Foydalanish", callback_data="info_usage")
            ],
            [
                InlineKeyboardButton(text="👁️ Ko'z kasalliklari", callback_data="info_diseases")
            ],
            [
                InlineKeyboardButton(text="🩺 Profilaktika", callback_data="info_prevention")
            ],
            [
                InlineKeyboardButton(text="❓ Ko'p so'raladigan savollar", callback_data="info_faq")
            ],
            [
                InlineKeyboardButton(text="📞 Bog'lanish", callback_data="info_contact")
            ],
            [
                InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="main_menu")
            ]
        ])
    
    @staticmethod
    def diseases_info() -> InlineKeyboardMarkup:
        """Kasalliklar haqida"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔵 Katarakta", callback_data="disease_cataract")
            ],
            [
                InlineKeyboardButton(text="👓 Miopiya", callback_data="disease_myopia")
            ],
            [
                InlineKeyboardButton(text="🔴 Glaukoma", callback_data="disease_glaucoma")
            ],
            [
                InlineKeyboardButton(text="🟡 Xorioretinit", callback_data="disease_chorioretinitis")
            ],
            [
                InlineKeyboardButton(text="🟣 To'r parda distrofiyasi", callback_data="disease_retinal")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="info")
            ]
        ])
    
    # ==================== CONFIRMATION ====================
    
    @staticmethod
    def confirm_action(confirm_callback: str, cancel_callback: str = "go_back") -> InlineKeyboardMarkup:
        """Amalni tasdiqlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=confirm_callback),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=cancel_callback)
            ]
        ])
    
    # ==================== REPLY KEYBOARDS ====================
    
    @staticmethod
    def phone_request() -> ReplyKeyboardMarkup:
        """Telefon raqamini so'rash"""
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    @staticmethod
    def location_request() -> ReplyKeyboardMarkup:
        """Joylashuvni so'rash"""
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)],
                [KeyboardButton(text="❌ Bekor qilish")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    @staticmethod
    def remove_keyboard() -> ReplyKeyboardRemove:
        """Klaviaturani olib tashlash"""
        return ReplyKeyboardRemove()
    
    # ==================== SPECIAL BUTTONS ====================
    
    @staticmethod
    def share_button(url: str) -> InlineKeyboardMarkup:
        """Ulashish tugmasi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📤 Do'stlarga ulashish", switch_inline_query=url)
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    @staticmethod
    def url_button(url: str, text: str = "🔗 Havolani ochish") -> InlineKeyboardMarkup:
        """URL tugmasi"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=text, url=url)],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")]
        ])


# ==================== SCREENING SPECIFIC KEYBOARDS ====================

class ScreeningKeyboards:
    """Skrining jarayoni uchun maxsus klaviaturalar"""
    
    @staticmethod
    def severity_selection() -> InlineKeyboardMarkup:
        """Jiddiylik darajasini tanlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="😊 Yengil", callback_data="severity_mild"),
                InlineKeyboardButton(text="😐 O'rtacha", callback_data="severity_moderate")
            ],
            [
                InlineKeyboardButton(text="😟 Og'ir", callback_data="severity_severe")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    @staticmethod
    def duration_selection() -> InlineKeyboardMarkup:
        """Muddatni tanlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 1 haftadan kam", callback_data="duration_week"),
                InlineKeyboardButton(text="📅 1 oydan kam", callback_data="duration_month")
            ],
            [
                InlineKeyboardButton(text="📅 1-6 oy", callback_data="duration_6months"),
                InlineKeyboardButton(text="📅 6 oydan ko'p", callback_data="duration_long")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    @staticmethod
    def age_selection() -> InlineKeyboardMarkup:
        """Yosh guruhini tanlash"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👶 18 dan kichik", callback_data="age_under18"),
                InlineKeyboardButton(text="🧑 18-40", callback_data="age_18_40")
            ],
            [
                InlineKeyboardButton(text="🧓 40-60", callback_data="age_40_60"),
                InlineKeyboardButton(text="👴 60+", callback_data="age_over60")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    @staticmethod
    def cataract_symptoms_detailed() -> InlineKeyboardMarkup:
        """Katarakta simptomlari batafsil"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌫️ Xira ko'rish", callback_data="symptom_blurry")
            ],
            [
                InlineKeyboardButton(text="🌈 Ranglar o'zgarishi", callback_data="symptom_color_change")
            ],
            [
                InlineKeyboardButton(text="🌙 Kechasi yomon ko'rish", callback_data="symptom_night_vision")
            ],
            [
                InlineKeyboardButton(text="☀️ Yorug'likka sezgirlik", callback_data="symptom_light_sensitive")
            ],
            [
                InlineKeyboardButton(text="👓 Ko'zoynakni tez-tez almashtirish", callback_data="symptom_glasses")
            ],
            [
                InlineKeyboardButton(text="✅ Barchasi", callback_data="symptom_all"),
                InlineKeyboardButton(text="❌ Hech biri", callback_data="symptom_none")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    @staticmethod
    def myopia_symptoms_detailed() -> InlineKeyboardMarkup:
        """Miopiya simptomlari batafsil"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Kitobga yaqin qarash", callback_data="symptom_close_reading")
            ],
            [
                InlineKeyboardButton(text="📺 TV yaqindan ko'rish", callback_data="symptom_close_tv")
            ],
            [
                InlineKeyboardButton(text="🎯 Uzoqni ko'rmaslık", callback_data="symptom_distant")
            ],
            [
                InlineKeyboardButton(text="🔍 Ko'zni qisish", callback_data="symptom_squinting")
            ],
            [
                InlineKeyboardButton(text="😫 Bosh og'rishi", callback_data="symptom_headache")
            ],
            [
                InlineKeyboardButton(text="✅ Barchasi", callback_data="symptom_all"),
                InlineKeyboardButton(text="❌ Hech biri", callback_data="symptom_none")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])
    
    @staticmethod
    def glaucoma_symptoms_detailed() -> InlineKeyboardMarkup:
        """Glaukoma simptomlari batafsil"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👁️ Ko'z bosimi", callback_data="symptom_eye_pressure")
            ],
            [
                InlineKeyboardButton(text="🌈 Halqalar ko'rish", callback_data="symptom_halos")
            ],
            [
                InlineKeyboardButton(text="📍 Yon tomondan ko'rmaslik", callback_data="symptom_peripheral_loss")
            ],
            [
                InlineKeyboardButton(text="🔴 Ko'z og'rishi", callback_data="symptom_eye_pain")
            ],
            [
                InlineKeyboardButton(text="🤢 Ko'ngil aynish", callback_data="symptom_nausea")
            ],
            [
                InlineKeyboardButton(text="✅ Barchasi", callback_data="symptom_all"),
                InlineKeyboardButton(text="❌ Hech biri", callback_data="symptom_none")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="go_back")
            ]
        ])


# Export
keyboards = Keyboards()
screening_keyboards = ScreeningKeyboards()
