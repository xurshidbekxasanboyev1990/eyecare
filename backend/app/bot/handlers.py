"""
==============================================================================
EyeCare Backend - Telegram Bot
==============================================================================
Aiogram 3.x based Telegram bot for eye screening with Web App integration.
"""

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from loguru import logger
import asyncio

from app.core.config import settings, MEDICATION_RECOMMENDATIONS, DISCLAIMER_MESSAGE


# ==============================================================================
# Bot States (FSM)
# ==============================================================================

class ScreeningStates(StatesGroup):
    """Screening flow states"""
    gender = State()
    eye_fatigue = State()
    foggy_vision = State()
    age_for_cataract = State()
    burning = State()
    distant_blur = State()
    peripheral_darkness = State()
    floaters = State()
    daltonism_confirm = State()
    complaint_menu = State()
    awaiting_test_result = State()


# ==============================================================================
# Text Messages (Uzbek)
# ==============================================================================

MESSAGES = {
    "welcome": """
🏥 *EyeCare Ko'z Tekshiruvi Botiga Xush Kelibsiz!*

Bu bot orqali siz quyidagi ko'z kasalliklarini tekshirishingiz mumkin:
• 👁 Miopiya (Yaqindan ko'rish)
• 🔵 Glaukoma
• 🌫 Katarakta
• 🔴 Xorioretinit
• 📐 To'r parda distrofiyasi

Barcha testlar 5 metr masofadan, birinchi o'ng ko'zni (chapni berkitib), keyin chap ko'zni (o'ngni berkitib) tekshirish asosida amalga oshiriladi.

Boshlash uchun /start tugmasini bosing yoki quyidagi menyudan foydalaning.
""",

    "gender_question": "👤 *Jinsingizni tanlang:*",
    
    "fatigue_question": """
😓 *Ko'zingizda toliqish his qilasizmi?*

Kunlik faoliyat davomida ko'z toliqishi, og'irlik yoki zo'riqish sezasizmi?
""",

    "foggy_question": """
🌫 *Atrofni go'yoki xira tuman yoki kirlangan oyna ortidan ko'rayotgandek his qilasizmi?*

Bu ko'rish xiralashuvini anglaydi.
""",

    "burning_question": """
🔥 *Ko'zingizda achishish his qilasizmi?*

Ko'z quruqligi, achishish yoki yonish sezasizmi?
""",

    "distant_blur_question": """
👓 *Uzoqdagi narsalarni ko'rishga qiynalasiz, lekin yaqindagi kitob yoki telefonni bemalol ko'ra olasizmi?*

Bu miopiya (yaqindan ko'rish) belgisi bo'lishi mumkin.
""",

    "peripheral_question": """
👁 *To'g'riga qarab turganingizda, chekka (yon) tomonlar tuman ichida yoki qorong'ulashib qolgandek tuyuladimi?*

Bu periferik ko'rish muammosi bo'lishi mumkin.
""",

    "floaters_question": """
✨ *Ko'zingiz oldida to'satdan paydo bo'lgan 'suzuvchi' qora dog'lar, chaqnashlar yoki ko'z ichida og'riq his qilasizmi?*

Bu to'r parda muammosi belgisi bo'lishi mumkin.
""",

    "age_question": "📅 *Yoshingizni kiriting:*",

    "daltonism_confirm": """
🎨 *Daltonizm testini ham topshirasizmi?*

Bu rang ajratish qobiliyatini tekshiradi.
""",

    "complaint_menu": """
📋 *Shikoyatingizni tanlang:*

Quyidagi ro'yxatdan sizga mos keladigan shikoyatni tanlang:
""",

    "test_intro": """
🔬 *{test_name} Testi*

Bu test {description}.

⚠️ *Muhim:*
• {distance}m masofadan o'tiring
• Yaxshi yoritilgan xonada bo'ling
• Birinchi o'ng ko'zni (chapni berkitib) tekshiring
• Keyin chap ko'zni (o'ngni berkitib) tekshiring

Tayyor bo'lgach, quyidagi tugmani bosing.
""",

    "result_header": """
📊 *Test Natijasi*

🔬 Test: {test_name}
📈 Natija: {status}
""",

    "recommendation_header": """
💊 *Tavsiyalar*

Sizda *{condition}* belgilari aniqlandi.

*Tavsiya etiladigan dorilar:*
""",

    "disclaimer": DISCLAIMER_MESSAGE
}


# ==============================================================================
# Keyboards
# ==============================================================================

def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👩 Ayol", callback_data="gender:female"),
            InlineKeyboardButton(text="👨 Erkak", callback_data="gender:male")
        ]
    ])


def get_frequency_keyboard() -> InlineKeyboardMarkup:
    """Frequency selection keyboard (No/Sometimes/Often)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Yo'q", callback_data="freq:no")],
        [InlineKeyboardButton(text="🔸 Ba'zan", callback_data="freq:sometimes")],
        [InlineKeyboardButton(text="🔹 Tez-tez", callback_data="freq:often")]
    ])


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Yes/No keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data="confirm:yes"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="confirm:no")
        ]
    ])


def get_complaint_menu_keyboard() -> InlineKeyboardMarkup:
    """Complaint selection menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="👓 Uzoqni yoki yaqinni xira ko'ryapman",
            callback_data="complaint:myopia"
        )],
        [InlineKeyboardButton(
            text="🌑 Yon tomonlarni ko'rmayapman",
            callback_data="complaint:glaucoma"
        )],
        [InlineKeyboardButton(
            text="📐 To'g'ri chiziqlar egri ko'rinyapti",
            callback_data="complaint:retinal"
        )],
        [InlineKeyboardButton(
            text="✨ Ko'z oldimda qora dog'lar bor",
            callback_data="complaint:chorioretinitis"
        )],
        [InlineKeyboardButton(
            text="🌫 Hamma narsa tuman ichidagidek",
            callback_data="complaint:cataract"
        )],
        [InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back:start"
        )]
    ])


def get_test_keyboard(test_type: str, web_app_url: str) -> InlineKeyboardMarkup:
    """Test start keyboard with Web App button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔬 Testni Boshlash",
            web_app=WebAppInfo(url=f"{web_app_url}?test={test_type}")
        )],
        [InlineKeyboardButton(
            text="⏭ O'tkazib yuborish",
            callback_data=f"skip:{test_type}"
        )],
        [InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back:menu"
        )]
    ])


def get_main_menu_keyboard(web_app_url: str) -> ReplyKeyboardMarkup:
    """Main menu reply keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🔬 Testni Boshlash",
                web_app=WebAppInfo(url=web_app_url)
            )],
            [
                KeyboardButton(text="📊 Natijalarim"),
                KeyboardButton(text="👨‍⚕️ Shifokorlar")
            ],
            [
                KeyboardButton(text="⚙️ Sozlamalar"),
                KeyboardButton(text="❓ Yordam")
            ]
        ],
        resize_keyboard=True
    )


def get_doctor_keyboard() -> InlineKeyboardMarkup:
    """Doctor contact keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📞 Shifokorga Qo'ng'iroq",
            callback_data="doctor:call"
        )],
        [InlineKeyboardButton(
            text="📅 Uchrashuv Belgilash",
            callback_data="doctor:appointment"
        )],
        [InlineKeyboardButton(
            text="🔙 Bosh Menyu",
            callback_data="back:start"
        )]
    ])


# ==============================================================================
# Bot Handlers Router
# ==============================================================================

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    # Get web app URL from settings
    web_app_url = settings.TELEGRAM_WEBAPP_URL
    if not web_app_url:
        web_app_url = "https://eyecare.uz"
    
    await message.answer(
        MESSAGES["welcome"],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(web_app_url)
    )
    
    # Start screening flow
    await message.answer(
        MESSAGES["gender_question"],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(ScreeningStates.gender)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = """
❓ *Yordam*

*Mavjud buyruqlar:*
/start - Botni qayta ishga tushirish
/test - Yangi test boshlash
/results - Natijalarni ko'rish
/doctors - Shifokorlar ro'yxati
/settings - Sozlamalar
/help - Yordam

*Testlar haqida:*
Barcha testlar 5 metr masofadan amalga oshiriladi. Har bir ko'zni alohida tekshiring.

*Muammo bo'lsa:*
@eyecare_support ga yozing.
"""
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("test"))
async def cmd_test(message: Message, state: FSMContext):
    """Handle /test command - start new screening"""
    await state.clear()
    await message.answer(
        MESSAGES["gender_question"],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(ScreeningStates.gender)


# ==============================================================================
# Screening Flow Handlers
# ==============================================================================

@router.callback_query(F.data.startswith("gender:"))
async def handle_gender(callback: CallbackQuery, state: FSMContext):
    """Handle gender selection"""
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    
    await callback.message.edit_text(
        MESSAGES["fatigue_question"],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_frequency_keyboard()
    )
    await state.set_state(ScreeningStates.eye_fatigue)
    await callback.answer()


@router.callback_query(ScreeningStates.eye_fatigue, F.data.startswith("freq:"))
async def handle_fatigue(callback: CallbackQuery, state: FSMContext):
    """Handle eye fatigue question"""
    answer = callback.data.split(":")[1]
    await state.update_data(eye_fatigue=answer)
    
    # Move to foggy vision question (Cataract screening)
    await callback.message.edit_text(
        MESSAGES["foggy_question"],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_frequency_keyboard()
    )
    await state.set_state(ScreeningStates.foggy_vision)
    await callback.answer()


@router.callback_query(ScreeningStates.foggy_vision, F.data.startswith("freq:"))
async def handle_foggy_vision(callback: CallbackQuery, state: FSMContext):
    """Handle foggy vision question - Cataract screening"""
    answer = callback.data.split(":")[1]
    await state.update_data(foggy_vision=answer)
    
    if answer in ["sometimes", "often"]:
        # Suspected cataract - ask for age and send contrast test
        await callback.message.edit_text(
            MESSAGES["age_question"],
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(ScreeningStates.age_for_cataract)
    else:
        # No cataract symptoms - proceed to burning question
        await callback.message.edit_text(
            MESSAGES["burning_question"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_frequency_keyboard()
        )
        await state.set_state(ScreeningStates.burning)
    
    await callback.answer()


@router.message(ScreeningStates.age_for_cataract)
async def handle_age_for_cataract(message: Message, state: FSMContext):
    """Handle age input for cataract screening"""
    try:
        age = int(message.text.strip())
        if age < 1 or age > 120:
            raise ValueError("Invalid age")
        
        await state.update_data(age=age)
        
        # Send cataract/contrast test
        web_app_url = settings.TELEGRAM_WEBAPP_URL or "https://eyecare.uz"
                description="kontrast ko'rish qobiliyatini tekshiradi. 9 ta turli xiralik va rangli filtrlar bilan test",
                distance="1"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_test_keyboard("contrast", web_app_url)
        )
        await state.set_state(ScreeningStates.awaiting_test_result)
        await state.update_data(current_test="cataract")
        
    except ValueError:
        await message.answer(
            "❌ Iltimos, to'g'ri yosh kiriting (1-120):",
            parse_mode=ParseMode.MARKDOWN
        )


@router.callback_query(ScreeningStates.burning, F.data.startswith("freq:"))
async def handle_burning(callback: CallbackQuery, state: FSMContext):
    """Handle burning question"""
    answer = callback.data.split(":")[1]
    await state.update_data(burning=answer)
    
    if answer == "sometimes":
        # Possible Myopia/Glaucoma - ask distant blur
        await callback.message.edit_text(
            MESSAGES["distant_blur_question"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_frequency_keyboard()
        )
        await state.set_state(ScreeningStates.distant_blur)
    elif answer == "often":
        # Possible Chorioretinitis/Retinal - ask about floaters
        await callback.message.edit_text(
            MESSAGES["floaters_question"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_frequency_keyboard()
        )
        await state.set_state(ScreeningStates.floaters)
    else:
        # No symptoms - show complaint menu
        await callback.message.edit_text(
            MESSAGES["complaint_menu"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_complaint_menu_keyboard()
        )
        await state.set_state(ScreeningStates.complaint_menu)
    
    await callback.answer()


@router.callback_query(ScreeningStates.distant_blur, F.data.startswith("freq:"))
async def handle_distant_blur(callback: CallbackQuery, state: FSMContext):
    """Handle distant blur question - Myopia screening"""
    answer = callback.data.split(":")[1]
    await state.update_data(distant_blur=answer)
    
    if answer in ["sometimes", "often"]:
        # Send Myopia test
        data = await state.get_data()
        age = data.get("age", 25)
        
        web_app_url = settings.TELEGRAM_WEBAPP_URL or "https://eyecare.uz"
        
        await callback.message.edit_text(
            MESSAGES["test_intro"].format(
                test_name="Miopiya (Snellen Sivsev testi)",
                description="uzoqdan ko'rish o'tkirligini tekshiradi",
                distance="5"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_test_keyboard("myopia", web_app_url)
        )
        await state.set_state(ScreeningStates.awaiting_test_result)
        await state.update_data(current_test="myopia")
    else:
        # No myopia - check for glaucoma
        await callback.message.edit_text(
            MESSAGES["peripheral_question"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_frequency_keyboard()
        )
        await state.set_state(ScreeningStates.peripheral_darkness)
    
    await callback.answer()


@router.callback_query(ScreeningStates.peripheral_darkness, F.data.startswith("freq:"))
async def handle_peripheral(callback: CallbackQuery, state: FSMContext):
    """Handle peripheral vision question - Glaucoma screening"""
    answer = callback.data.split(":")[1]
    await state.update_data(peripheral_darkness=answer)
    
    if answer in ["sometimes", "often"]:
        # Send Glaucoma test (Perimetry)
        web_app_url = settings.TELEGRAM_WEBAPP_URL or "https://eyecare.uz"
        
        await callback.message.edit_text(
            MESSAGES["test_intro"].format(
                test_name="Glaukoma (Perimetriya)",
                description="periferik ko'rishni tekshiradi. 9 ta nuqta koordinatalari (10,10) dan (30,30) gacha",
                distance="0.5"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_test_keyboard("perimetry", web_app_url)
        )
        await state.set_state(ScreeningStates.awaiting_test_result)
        await state.update_data(current_test="glaucoma")
    else:
        # Show complaint menu
        await callback.message.edit_text(
            MESSAGES["complaint_menu"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_complaint_menu_keyboard()
        )
        await state.set_state(ScreeningStates.complaint_menu)
    
    await callback.answer()


@router.callback_query(ScreeningStates.floaters, F.data.startswith("freq:"))
async def handle_floaters(callback: CallbackQuery, state: FSMContext):
    """Handle floaters question - Chorioretinitis screening"""
    answer = callback.data.split(":")[1]
    await state.update_data(floaters=answer)
    
    if answer in ["sometimes", "often"]:
        # Ask age and send Chorioretinitis test
        await callback.message.edit_text(
            MESSAGES["age_question"],
            parse_mode=ParseMode.MARKDOWN
        )
        # Store that we need chorioretinitis test after age
        await state.update_data(pending_test="chorioretinitis")
        await state.set_state(ScreeningStates.age_for_cataract)  # Reuse age state
    else:
        # Show complaint menu
        await callback.message.edit_text(
            MESSAGES["complaint_menu"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_complaint_menu_keyboard()
        )
        await state.set_state(ScreeningStates.complaint_menu)
    
    await callback.answer()


# ==============================================================================
# Complaint Menu Handlers
# ==============================================================================

@router.callback_query(F.data.startswith("complaint:"))
async def handle_complaint(callback: CallbackQuery, state: FSMContext):
    """Handle complaint menu selection"""
    complaint = callback.data.split(":")[1]
    web_app_url = settings.TELEGRAM_WEBAPP_URL or "https://eyecare.uz"
    
    test_configs = {
        "myopia": {
            "name": "Miopiya (Snellen Sivsev)",
            "description": "uzoqdan ko'rish o'tkirligini tekshiradi",
            "distance": "5",
            "test_type": "visual_acuity"
        },
        "glaucoma": {
            "name": "Glaukoma (Perimetriya)",
            "description": "periferik ko'rishni tekshiradi",
            "distance": "0.5",
            "test_type": "perimetry"
        },
        "retinal": {
            "name": "To'r Parda (Amsler To'ri)",
            "description": "to'r parda holatini tekshiradi. Egilgan, to'lqinli va qorong'ulashgan holatlarni aniqlaydi",
            "distance": "0.3",
            "test_type": "amsler"
        },
        "chorioretinitis": {
            "name": "Xorioretinit",
            "description": "ko'z tubi holatini tekshiradi",
            "distance": "0.5",
            "test_type": "red_desaturation"
        },
        "cataract": {
            "name": "Katarakta (Kontrast)",
            "description": "kontrast sezgirligini tekshiradi",
            "distance": "1",
            "test_type": "contrast"
        }
    }
    
    config = test_configs.get(complaint)
    if config:
        await callback.message.edit_text(
            MESSAGES["test_intro"].format(
                test_name=config["name"],
                description=config["description"],
                distance=config["distance"]
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_test_keyboard(config["test_type"], web_app_url)
        )
        await state.set_state(ScreeningStates.awaiting_test_result)
        await state.update_data(current_test=complaint)
    
    await callback.answer()


@router.callback_query(F.data.startswith("back:"))
async def handle_back(callback: CallbackQuery, state: FSMContext):
    """Handle back button"""
    target = callback.data.split(":")[1]
    
    if target == "start":
        await state.clear()
        await callback.message.edit_text(
            MESSAGES["gender_question"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(ScreeningStates.gender)
    elif target == "menu":
        await callback.message.edit_text(
            MESSAGES["complaint_menu"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_complaint_menu_keyboard()
        )
        await state.set_state(ScreeningStates.complaint_menu)
    
    await callback.answer()


# ==============================================================================
# Test Result Handlers
# ==============================================================================

@router.callback_query(F.data.startswith("skip:"))
async def handle_skip_test(callback: CallbackQuery, state: FSMContext):
    """Handle test skip"""
    await callback.message.edit_text(
        MESSAGES["complaint_menu"],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_complaint_menu_keyboard()
    )
    await state.set_state(ScreeningStates.complaint_menu)
    await callback.answer("Test o'tkazib yuborildi")


# ==============================================================================
# Medication Recommendations
# ==============================================================================

async def send_recommendations(message: Message, condition: str):
    """Send medication recommendations for detected condition"""
    meds = MEDICATION_RECOMMENDATIONS.get(condition)
    
    if not meds:
        return
    
    condition_names = {
        "myopia": "Miopiya",
        "glaucoma": "Glaukoma",
        "cataract": "Katarakta",
        "chorioretinitis": "Xorioretinit",
        "retinal_dystrophy": "To'r parda distrofiyasi"
    }
    
    text = MESSAGES["recommendation_header"].format(
        condition=condition_names.get(condition, condition)
    )
    
    for med in meds["medications"]:
        text += f"\n• *{med}*"
    
    text += f"\n\n_{meds['description']}_"
    text += f"\n💊 Qo'llash: {meds['usage']}"
    text += f"\n\n{MESSAGES['disclaimer']}"
    
    await message.answer(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_doctor_keyboard()
    )


# ==============================================================================
# Web App Data Handler
# ==============================================================================

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, state: FSMContext):
    """Handle data from Web App (test results)"""
    import json
    
    try:
        data = json.loads(message.web_app_data.data)
        logger.info(f"📊 Received Web App data: {data}")
        
        test_type = data.get("test_type")
        status = data.get("status", "unknown")
        score = data.get("score", "-")
        
        # Store result
        state_data = await state.get_data()
        current_test = state_data.get("current_test", test_type)
        
        # Send result message
        test_names = {
            "visual_acuity": "Ko'rish O'tkirligi",
            "contrast": "Kontrast Sezgirligi",
            "amsler": "Amsler Panjarasi",
            "perimetry": "Perimetriya",
            "color_blindness": "Daltonizm",
            "red_desaturation": "Qizil Desaturatsiya"
        }
        
        status_emoji = {
            "normal": "✅ Normal",
            "warning": "⚠️ Ehtiyotkor bo'ling",
            "concern": "🔴 Tekshiruv tavsiya etiladi"
        }
        
        result_text = MESSAGES["result_header"].format(
            test_name=test_names.get(test_type, test_type),
            status=status_emoji.get(status, status)
        )
        
        if score:
            result_text += f"\n📈 Ball: *{score}*"
        
        await message.answer(result_text, parse_mode=ParseMode.MARKDOWN)
        
        # If concerning, send recommendations
        if status in ["warning", "concern"]:
            # Map test_type to condition
            condition_map = {
                "visual_acuity": "myopia",
                "contrast": "cataract",
                "amsler": "retinal_dystrophy",
                "perimetry": "glaucoma",
                "red_desaturation": "chorioretinitis"
            }
            condition = condition_map.get(test_type, current_test)
            await send_recommendations(message, condition)
        
        # Ask about daltonism test after myopia
        if test_type == "visual_acuity":
            await message.answer(
                MESSAGES["daltonism_confirm"],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_yes_no_keyboard()
            )
            await state.set_state(ScreeningStates.daltonism_confirm)
        else:
            # Show complaint menu for more tests
            await message.answer(
                "🔄 Boshqa test topshirmoqchimisiz?",
                reply_markup=get_complaint_menu_keyboard()
            )
            await state.set_state(ScreeningStates.complaint_menu)
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Web App data: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.callback_query(ScreeningStates.daltonism_confirm, F.data.startswith("confirm:"))
async def handle_daltonism_confirm(callback: CallbackQuery, state: FSMContext):
    """Handle daltonism test confirmation"""
    answer = callback.data.split(":")[1]
    
    if answer == "yes":
        web_app_url = settings.TELEGRAM_WEBAPP_URL or "https://eyecare.uz"
                description="rang ajratish qobiliyatini tekshiradi",
                distance="0.75"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_test_keyboard("color_blindness", web_app_url)
        )
        await state.set_state(ScreeningStates.awaiting_test_result)
        await state.update_data(current_test="color_blindness")
    else:
        await callback.message.edit_text(
            MESSAGES["complaint_menu"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_complaint_menu_keyboard()
        )
        await state.set_state(ScreeningStates.complaint_menu)
    
    await callback.answer()


# ==============================================================================
# Text Message Handlers
# ==============================================================================

@router.message(F.text == "📊 Natijalarim")
async def handle_results_button(message: Message):
    """Handle results button"""
    await message.answer(
        "📊 Natijalaringizni ko'rish uchun /results buyrug'ini yuboring yoki Web App dan foydalaning.",
        parse_mode=ParseMode.MARKDOWN
    )


@router.message(F.text == "👨‍⚕️ Shifokorlar")
async def handle_doctors_button(message: Message):
    """Handle doctors button"""
    doctors_text = """
👨‍⚕️ *Tavsiya Etilgan Shifokorlar*

1️⃣ *Dr. Abdullayev Jasur*
   Oftalmolog | 15 yillik tajriba
   📍 Toshkent, Chilonzor
   📞 +998 71 123-45-67

2️⃣ *Dr. Karimova Nilufar*
   Oftalmolog | 10 yillik tajriba
   📍 Toshkent, Yunusobod
   📞 +998 71 234-56-78

Ko'proq shifokorlar uchun Web App dan foydalaning.
"""
    await message.answer(
        doctors_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_doctor_keyboard()
    )


@router.message(F.text == "⚙️ Sozlamalar")
async def handle_settings_button(message: Message):
    """Handle settings button"""
    settings_text = """
⚙️ *Sozlamalar*

🌐 Til: O'zbek
🔔 Bildirishnomalar: Yoqilgan
⏰ Eslatma: 180 kun

Sozlamalarni o'zgartirish uchun /settings buyrug'ini yuboring.
"""
    await message.answer(settings_text, parse_mode=ParseMode.MARKDOWN)


@router.message(F.text == "❓ Yordam")
async def handle_help_button(message: Message):
    """Handle help button"""
    await cmd_help(message)


# ==============================================================================
# Bot Initialization
# ==============================================================================

async def create_bot() -> tuple[Bot, Dispatcher]:
    """Create and configure bot instance"""
    if not settings.bot_token:
        raise ValueError("BOT_TOKEN is not configured")
    
    bot = Bot(token=settings.bot_token)
    
    # Use in-memory storage for FSM (no Redis needed)
    storage = MemoryStorage()
    
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    
    return bot, dp


async def start_polling():
    """Start bot polling (for development)"""
    bot, dp = await create_bot()
    
    logger.info("🤖 Starting bot polling...")
    await dp.start_polling(bot)
