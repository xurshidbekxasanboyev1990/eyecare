"""
EyeCare Backend - Diagnosis Service

Tashxis va tavsiyalar generatsiyasi
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.test import TestResult, TestType


class DiagnosisService:
    """
    Ko'z kasalliklarini aniqlash va tavsiyalar berish uchun service
    
    Bu service Telegram bot va Web App uchun umumiy tashxis logikasini ta'minlaydi
    """
    
    # Kasalliklar va ularning belgilari
    DISEASES = {
        "cataract": {
            "name_uz": "Katarakta",
            "name_ru": "Катаракта",
            "symptoms": [
                "xira_korish",  # Xira ko'rish
                "rang_ozgarishi",  # Ranglarni ajrata olmaslik
                "kechasi_yomon",  # Kechasi yomon ko'rish
                "yoruglik_sezgirlik",  # Yorug'likka sezgirlik
                "ikki_korish"  # Ikkilangan ko'rish
            ],
            "risk_factors": ["yosh_60_plus", "diabet", "travma"],
            "medicines": [
                {
                    "name": "Tauforin 4%",
                    "dosage": "1-2 tomchi kuniga 3 mahal",
                    "duration": "1-3 oy"
                },
                {
                    "name": "Quinax",
                    "dosage": "1-2 tomchi kuniga 3-5 mahal",
                    "duration": "Doimiy"
                }
            ],
            "recommendations": [
                "Oftalmolog ko'rigidan o'ting",
                "Quyosh nuri va UV nurlardan himoyalaning",
                "Antioksidantlarga boy ovqatlar iste'mol qiling",
                "Chekishni to'xtating"
            ]
        },
        "myopia": {
            "name_uz": "Miopiya (Yaqindan ko'rish)",
            "name_ru": "Миопия (Близорукость)",
            "symptoms": [
                "uzoqni_kormaslik",
                "bosh_ogrigi",
                "kozni_qisish",
                "charchoq"
            ],
            "risk_factors": ["genetika", "yaqindan_ish", "kam_yoruglik"],
            "medicines": [
                {
                    "name": "Irifrin 2.5%",
                    "dosage": "1 tomchi kechqurun",
                    "duration": "1 oy kurs"
                },
                {
                    "name": "Emoxipin 1%",
                    "dosage": "1-2 tomchi kuniga 2-3 mahal",
                    "duration": "10-30 kun"
                }
            ],
            "recommendations": [
                "Ko'zoynakni to'g'ri tanlang",
                "20-20-20 qoidasiga rioya qiling",
                "Tabiiy yorug'likda ishlang",
                "Ko'z mashqlarini bajaring"
            ]
        },
        "glaucoma": {
            "name_uz": "Glaukoma",
            "name_ru": "Глаукома",
            "symptoms": [
                "koz_bosimi",
                "periferik_korish_yoqolishi",
                "halqalar_korish",
                "koz_ogrigi",
                "bosh_ogrigi"
            ],
            "risk_factors": ["yosh_40_plus", "oilaviy_tarix", "yuqori_koz_bosimi"],
            "medicines": [
                {
                    "name": "Timolol 0.5%",
                    "dosage": "1 tomchi kuniga 2 mahal",
                    "duration": "Doimiy"
                },
                {
                    "name": "Arutimol 0.5%",
                    "dosage": "1 tomchi kuniga 2 mahal",
                    "duration": "Doimiy"
                },
                {
                    "name": "Latanoprost",
                    "dosage": "1 tomchi kechqurun",
                    "duration": "Doimiy"
                }
            ],
            "recommendations": [
                "ZUDLIK BILAN oftalmologga murojaat qiling!",
                "Ko'z bosimini muntazam tekshiring",
                "Dorilarni to'xtatmang",
                "Og'ir jismoniy mehnatdan saqlaning"
            ]
        },
        "chorioretinitis": {
            "name_uz": "Xorioretinit",
            "name_ru": "Хориоретинит",
            "symptoms": [
                "korish_xiralashishi",
                "qorongulashgan_dog_korish",
                "rang_qabul_qilish_buzilishi",
                "metamorfopsiya"
            ],
            "risk_factors": ["infektsiya", "autoimmun_kasallik", "travma"],
            "medicines": [
                {
                    "name": "Deksametazon 0.1%",
                    "dosage": "1-2 tomchi kuniga 4-6 mahal",
                    "duration": "Shifokor ko'rsatmasi bilan"
                },
                {
                    "name": "Retinalamin",
                    "dosage": "5mg kuniga 1 mahal (in'ektsiya)",
                    "duration": "10 kun kurs"
                }
            ],
            "recommendations": [
                "Oftalmologga zudlik bilan murojaat qiling",
                "Infektsiya manbasini aniqlang",
                "Davolanish kursini to'liq o'tkazing",
                "Ko'zni mexanik ta'sirdan himoyalang"
            ]
        },
        "retinal_dystrophy": {
            "name_uz": "To'r parda distrofiyasi",
            "name_ru": "Дистрофия сетчатки",
            "symptoms": [
                "markaziy_korish_buzilishi",
                "tekis_chiziqlar_egri_korish",
                "qorong_adaptatsiya_buzilishi",
                "rang_idrok_buzilishi"
            ],
            "risk_factors": ["yosh_50_plus", "genetika", "quyosh_nuri"],
            "medicines": [
                {
                    "name": "Retinalamin",
                    "dosage": "5mg kuniga 1 mahal",
                    "duration": "10 kun kurs"
                },
                {
                    "name": "Tauforin 4%",
                    "dosage": "1-2 tomchi kuniga 3 mahal",
                    "duration": "3 oy"
                },
                {
                    "name": "Lutein kompleks",
                    "dosage": "1 tabletka kuniga 1 mahal",
                    "duration": "2 oy"
                }
            ],
            "recommendations": [
                "Oftalmologga murojaat qiling",
                "Lutein va zeaksantin qabul qiling",
                "UV himoya ko'zoynak taqing",
                "Qon bosimini nazorat qiling"
            ]
        }
    }
    
    # Dorilar haqida umumiy ma'lumot
    MEDICINE_INFO = {
        "Tauforin 4%": {
            "description": "Taurin asosidagi ko'z tomchisi, ko'z to'qimalarini oziqlantiradi",
            "contraindications": "Individual intolerantlik",
            "side_effects": "Kamdan-kam allergik reaktsiyalar"
        },
        "Timolol 0.5%": {
            "description": "Beta-bloker, ko'z ichidagi bosimni tushiradi",
            "contraindications": "Astma, bradikardiya, yurak yetishmovchiligi",
            "side_effects": "Ko'z quruqligi, bosh aylanishi"
        },
        "Deksametazon 0.1%": {
            "description": "Kortikosteroid, yallig'lanishga qarshi",
            "contraindications": "Virusli infektsiyalar, glaukoma",
            "side_effects": "Uzoq muddatli ishlatishda ko'z bosimi oshishi"
        },
        "Retinalamin": {
            "description": "Peptid preparati, to'r pardani himoyalaydi",
            "contraindications": "Individual intolerantlik, homiladorlik",
            "side_effects": "In'ektsiya joyida og'riq"
        },
        "Arutimol 0.5%": {
            "description": "Beta-bloker, ko'z ichidagi bosimni tushiradi",
            "contraindications": "Astma, bradikardiya",
            "side_effects": "Ko'z quruqligi, bosh og'rigi"
        }
    }
    
    # Test natijalarini baholash mezonlari
    TEST_THRESHOLDS = {
        TestType.VISUAL_ACUITY: {
            "excellent": 100,  # 20/20 yoki yaxshiroq
            "good": 80,       # 20/25
            "fair": 60,       # 20/30 - 20/40
            "poor": 40        # 20/50 yoki yomonroq
        },
        TestType.COLOR_BLINDNESS: {
            "normal": 90,     # 90%+ to'g'ri
            "mild_deficiency": 70,
            "moderate_deficiency": 50,
            "severe_deficiency": 30
        },
        TestType.ASTIGMATISM: {
            "none": 100,
            "mild": 70,
            "moderate": 50,
            "severe": 30
        },
        TestType.AMSLER_GRID: {
            "normal": 100,
            "mild_distortion": 70,
            "moderate_distortion": 50,
            "severe_distortion": 30
        },
        TestType.CONTRAST: {
            "excellent": 90,
            "good": 70,
            "fair": 50,
            "poor": 30
        }
    }
    
    @classmethod
    def analyze_results(
        cls,
        test_results: List[TestResult],
        symptoms: Optional[List[str]] = None,
        risk_factors: Optional[List[str]] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test natijalarini tahlil qilish va tashxis berish
        """
        analysis = {
            "overall_score": 0,
            "risk_level": "low",
            "detected_issues": [],
            "suspected_conditions": [],
            "recommendations": [],
            "medicines": [],
            "urgency": "routine"
        }
        
        if not test_results:
            return analysis
        
        # Calculate overall score (score is stored as string)
        scores = []
        for r in test_results:
            try:
                scores.append(float(r.score) if r.score else 0)
            except (ValueError, TypeError):
                scores.append(0)
        
        analysis["overall_score"] = round(sum(scores) / len(scores), 2) if scores else 0
        
        # Analyze each test result
        issues = []
        for result in test_results:
            issue = cls._analyze_single_test(result)
            if issue:
                issues.append(issue)
        
        analysis["detected_issues"] = issues
        
        # Determine suspected conditions based on symptoms and test results
        suspected = cls._detect_conditions(issues, symptoms or [], risk_factors or [])
        analysis["suspected_conditions"] = suspected
        
        # Generate recommendations
        analysis["recommendations"] = cls._generate_recommendations(
            suspected, issues, age
        )
        
        # Get medicine recommendations
        analysis["medicines"] = cls._get_medicine_recommendations(suspected)
        
        # Determine risk level and urgency
        analysis["risk_level"], analysis["urgency"] = cls._assess_risk(
            suspected, issues, analysis["overall_score"]
        )
        
        return analysis
    
    @classmethod
    def _analyze_single_test(cls, result: TestResult) -> Optional[Dict[str, Any]]:
        """
        Bitta test natijasini tahlil qilish
        """
        test_type = result.test_type
        try:
            score = float(result.score) if result.score else 0
        except (ValueError, TypeError):
            score = 0
        
        if test_type not in cls.TEST_THRESHOLDS:
            return None
        
        thresholds = cls.TEST_THRESHOLDS[test_type]
        
        # Determine severity based on score
        if score >= list(thresholds.values())[0]:
            severity = "normal"
        elif score >= list(thresholds.values())[1]:
            severity = "mild"
        elif score >= list(thresholds.values())[2]:
            severity = "moderate"
        else:
            severity = "severe"
        
        if severity == "normal":
            return None
        
        return {
            "test_type": test_type.value,
            "score": score,
            "severity": severity,
            "eye": result.eye_side.value if result.eye_side else None,
            "description": cls._get_issue_description(test_type, severity)
        }
    
    @classmethod
    def _get_issue_description(cls, test_type: TestType, severity: str) -> str:
        """
        Muammo tavsifini olish
        """
        descriptions = {
            TestType.VISUAL_ACUITY: {
                "mild": "Ko'rish keskinligi biroz pasaygan",
                "moderate": "Ko'rish keskinligi sezilarli pasaygan",
                "severe": "Ko'rish keskinligi jiddiy pasaygan"
            },
            TestType.COLOR_BLINDNESS: {
                "mild": "Engil rang ajratish qiyinchiligi",
                "moderate": "O'rtacha rang ko'rligi belgilari",
                "severe": "Jiddiy rang ko'rligi"
            },
            TestType.ASTIGMATISM: {
                "mild": "Engil astigmatizm belgilari",
                "moderate": "O'rtacha astigmatizm",
                "severe": "Jiddiy astigmatizm"
            },
            TestType.AMSLER_GRID: {
                "mild": "Engil makulyar o'zgarishlar",
                "moderate": "O'rtacha makulyar degeneratsiya belgilari",
                "severe": "Jiddiy makulyar buzilish"
            },
            TestType.CONTRAST: {
                "mild": "Kontrast sezgirligi biroz pasaygan",
                "moderate": "Kontrast sezgirligi sezilarli pasaygan",
                "severe": "Kontrast sezgirligi jiddiy pasaygan"
            }
        }
        
        return descriptions.get(test_type, {}).get(severity, "Anomaliya aniqlandi")
    
    @classmethod
    def _detect_conditions(
        cls,
        issues: List[Dict],
        symptoms: List[str],
        risk_factors: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Kasalliklarni aniqlash
        """
        suspected = []
        
        for disease_key, disease_info in cls.DISEASES.items():
            score = 0
            matched_symptoms = []
            
            # Check symptoms
            for symptom in symptoms:
                if symptom in disease_info["symptoms"]:
                    score += 2
                    matched_symptoms.append(symptom)
            
            # Check risk factors
            for factor in risk_factors:
                if factor in disease_info["risk_factors"]:
                    score += 1
            
            # Check test results
            for issue in issues:
                if disease_key == "myopia" and issue["test_type"] == "visual_acuity":
                    score += 2 if issue["severity"] in ["moderate", "severe"] else 1
                elif disease_key == "cataract" and issue["test_type"] in ["visual_acuity", "contrast"]:
                    score += 1
                elif disease_key == "glaucoma" and issue["test_type"] == "perimetry":
                    score += 3
                elif disease_key == "retinal_dystrophy" and issue["test_type"] == "amsler_grid":
                    score += 3
            
            if score >= 3:
                suspected.append({
                    "key": disease_key,
                    "name": disease_info["name_uz"],
                    "probability": min(score * 15, 90),
                    "matched_symptoms": matched_symptoms
                })
        
        # Sort by probability
        suspected.sort(key=lambda x: x["probability"], reverse=True)
        
        return suspected[:3]  # Return top 3
    
    @classmethod
    def _generate_recommendations(
        cls,
        suspected: List[Dict],
        issues: List[Dict],
        age: Optional[int]
    ) -> List[str]:
        """
        Tavsiyalar generatsiyasi
        """
        recommendations = []
        
        # General recommendations
        recommendations.append("Oftalmolog shifokorga murojaat qiling")
        
        # Age-specific
        if age:
            if age >= 40:
                recommendations.append("40 yoshdan keyin yillik ko'z tekshiruvi tavsiya etiladi")
            if age >= 60:
                recommendations.append("Katarakta va glaukoma riski yuqori - muntazam tekshiruv zarur")
        
        # Condition-specific recommendations
        for condition in suspected:
            disease_info = cls.DISEASES.get(condition["key"], {})
            recommendations.extend(disease_info.get("recommendations", [])[:2])
        
        # Issue-specific
        for issue in issues:
            if issue["test_type"] == "visual_acuity" and issue["severity"] in ["moderate", "severe"]:
                recommendations.append("Ko'zoynakni tekshirish yoki yangilash kerak")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:7]
    
    @classmethod
    def _get_medicine_recommendations(
        cls,
        suspected: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Dori tavsiyalari
        """
        medicines = []
        seen_medicines = set()
        
        for condition in suspected:
            disease_info = cls.DISEASES.get(condition["key"], {})
            
            for med in disease_info.get("medicines", []):
                if med["name"] not in seen_medicines:
                    seen_medicines.add(med["name"])
                    medicine_entry = {
                        "name": med["name"],
                        "dosage": med["dosage"],
                        "duration": med["duration"],
                        "for_condition": disease_info["name_uz"]
                    }
                    
                    # Add additional info if available
                    if med["name"] in cls.MEDICINE_INFO:
                        medicine_entry.update(cls.MEDICINE_INFO[med["name"]])
                    
                    medicines.append(medicine_entry)
        
        return medicines
    
    @classmethod
    def _assess_risk(
        cls,
        suspected: List[Dict],
        issues: List[Dict],
        overall_score: float
    ) -> tuple:
        """
        Risk darajasini aniqlash
        """
        # Check for high-risk conditions
        high_risk_conditions = ["glaucoma"]
        moderate_risk_conditions = ["cataract", "retinal_dystrophy", "chorioretinitis"]
        
        for condition in suspected:
            if condition["key"] in high_risk_conditions and condition["probability"] >= 60:
                return ("high", "urgent")
            if condition["key"] in moderate_risk_conditions and condition["probability"] >= 70:
                return ("moderate", "soon")
        
        # Check severity of issues
        severe_issues = [i for i in issues if i["severity"] == "severe"]
        moderate_issues = [i for i in issues if i["severity"] == "moderate"]
        
        if len(severe_issues) >= 2 or overall_score < 40:
            return ("high", "urgent")
        elif len(severe_issues) >= 1 or len(moderate_issues) >= 2 or overall_score < 60:
            return ("moderate", "soon")
        elif len(moderate_issues) >= 1 or overall_score < 75:
            return ("low", "routine")
        
        return ("minimal", "routine")
    
    @classmethod
    def generate_diagnosis_text(
        cls,
        analysis: Dict[str, Any],
        language: str = "uz"
    ) -> str:
        """
        Tashxis matnini generatsiya qilish
        """
        lines = []
        
        # Header
        lines.append("🏥 KO'Z TEKSHIRUVI NATIJALARI")
        lines.append("=" * 30)
        lines.append("")
        
        # Overall score
        score = analysis["overall_score"]
        if score >= 80:
            status = "✅ Yaxshi"
        elif score >= 60:
            status = "⚠️ O'rtacha"
        else:
            status = "🔴 Diqqat talab"
        
        lines.append(f"📊 Umumiy ball: {score}/100 - {status}")
        lines.append(f"⚡ Risk darajasi: {analysis['risk_level'].upper()}")
        lines.append("")
        
        # Detected issues
        if analysis["detected_issues"]:
            lines.append("🔍 ANIQLANGAN MUAMMOLAR:")
            for issue in analysis["detected_issues"]:
                eye_text = f" ({issue['eye']} ko'z)" if issue.get("eye") else ""
                lines.append(f"  • {issue['description']}{eye_text}")
            lines.append("")
        
        # Suspected conditions
        if analysis["suspected_conditions"]:
            lines.append("⚠️ EHTIMOLIY HOLATLAR:")
            for condition in analysis["suspected_conditions"]:
                lines.append(f"  • {condition['name']} - {condition['probability']}% ehtimol")
            lines.append("")
        
        # Recommendations
        if analysis["recommendations"]:
            lines.append("📋 TAVSIYALAR:")
            for rec in analysis["recommendations"]:
                lines.append(f"  • {rec}")
            lines.append("")
        
        # Medicines
        if analysis["medicines"]:
            lines.append("💊 DORI TAVSIYALARI:")
            lines.append("⚠️ DIQQAT: Dorilar faqat shifokor ko'rsatmasi bilan!")
            lines.append("")
            for med in analysis["medicines"]:
                lines.append(f"  💊 {med['name']}")
                lines.append(f"     Dozasi: {med['dosage']}")
                lines.append(f"     Muddati: {med['duration']}")
                lines.append(f"     Holat uchun: {med['for_condition']}")
                lines.append("")
        
        # Disclaimer
        lines.append("=" * 30)
        lines.append("⚠️ MUHIM ESLATMA:")
        lines.append("Bu natijalar faqat dastlabki tekshiruvdir.")
        lines.append("Aniq tashxis va davolash uchun oftalmolog")
        lines.append("shifokorga murojaat qilishingiz SHART!")
        lines.append("")
        lines.append(f"📅 Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        return "\n".join(lines)
    
    @classmethod
    def get_disease_info(cls, disease_key: str) -> Optional[Dict[str, Any]]:
        """
        Kasallik haqida ma'lumot olish
        """
        return cls.DISEASES.get(disease_key)
    
    @classmethod
    def get_medicine_details(cls, medicine_name: str) -> Optional[Dict[str, Any]]:
        """
        Dori haqida batafsil ma'lumot
        """
        return cls.MEDICINE_INFO.get(medicine_name)
