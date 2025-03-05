from openai import AsyncOpenAI
from typing import TypedDict, List
import asyncio

class Requirements(TypedDict):
    practical: List[str]
    solution: List[str]
    timeline: List[str]
    award_criteria: List[str]
    price: List[str]

client = AsyncOpenAI()

async def extract_requirements(text: str, language: str) -> Requirements:
    practical, solution, timeline, award_criteria, price = await asyncio.gather(
        extract_practical_requirements(text, language),
        extract_solution_requirements(text, language),
        extract_timeline_requirements(text, language),
        extract_award_criteria(text, language),
        extract_price_information(text, language)
    )

    system_content = {
        'en': "Convert the provided sections into a JSON format with arrays. Each bullet point should become an array item. Remove the bullet points (•) and any extra whitespace. If a section is empty or contains no bullet points, return an empty array for that section.",
        'dk': "Konverter de angivne sektioner til JSON-format med arrays. Hvert punkt skal blive til et array-element. Fjern punkttegn (•) og ekstra mellemrum. Hvis en sektion er tom eller ikke indeholder punkter, returnér et tomt array for den sektion."
    }

    user_content = {
        'en': f"""Convert these sections into JSON arrays. Return empty arrays for any sections without data:

PRACTICAL:
{practical}

SOLUTION:
{solution}

TIMELINE:
{timeline}

AWARD CRITERIA:
{award_criteria}

PRICE:
{price}

Format as:
{{
    "practical": ["requirement 1", "requirement 2", ...],
    "solution": ["spec 1", "spec 2", ...],
    "timeline": ["date 1: action", "date 2: action", ...],
    "award_criteria": ["criteria 1", "criteria 2", ...],
    "price": ["price info 1", "price info 2", ...]
}}

Important: Return empty arrays ([]) for any sections without bullet points or data.""",
        'dk': f"""Konverter disse sektioner til JSON arrays. Returnér tomme arrays for sektioner uden data:

PRAKTISK:
{practical}

LØSNING:
{solution}

TIDSLINJE:
{timeline}

TILDELINGSKRITERIER:
{award_criteria}

PRIS:
{price}

Formater som følgende:
{{
    "practical": ["krav 1", "krav 2", ...],
    "solution": ["spec 1", "spec 2", ...],
    "timeline": ["dato 1: handling", "dato 2: handling", ...],
    "award_criteria": ["kriterie 1", "kriterie 2", ...],
    "price": ["pris info 1", "pris info 2", ...]
}}

Vigtigt: Returnér tomme arrays ([]) for sektioner uden punkter eller data."""
    }

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_content.get(language, system_content['en'])
            },
            {
                "role": "user",
                "content": user_content.get(language, user_content['en'])
            }
        ]
    )

    default_response: Requirements = {
        "practical": [],
        "solution": [],
        "timeline": [],
        "award_criteria": [],
        "price": []
    }

    try:
        if completion.choices[0].message.content:
            return {**default_response, **eval(completion.choices[0].message.content)}
    except:
        pass
    
    return default_response

async def extract_practical_requirements(text: str, language: str) -> str:
    system_content = {
        'en': (
            "You are a detail-oriented analyst specializing in tender documents. "
            "Your task is to extract all administrative and procedural requirements related to tender submissions from the provided text. "
            "Each requirement must be formatted as a bullet point starting with '• '. "
            "If no applicable requirements are found, simply return an empty string without any additional commentary."
        ),
        'dk': (
            "Du er en detaljeorienteret analytiker specialiseret i udbudsdokumenter. "
            "Din opgave er at uddrage alle administrative og proceduremæssige krav relateret til udbudsindsendelser fra den givne tekst. "
            "Hvert krav skal formateres som et punkt startende med '• '. "
            "Hvis der ikke findes relevante krav, returnér blot en tom streng uden yderligere kommentarer."
        )
    }

    user_content = {
        'en': (
            "Please extract the administrative and procedural requirements for submitting this tender from the text below. "
            "Focus on items such as:\n"
            "• Document format rules (e.g., page limits, required sections)\n"
            "• Legal and licensing prerequisites\n"
            "• Submission methods (e.g., where and how to submit)\n"
            "• Required certifications or documentation\n"
            "• Insurance or bonding requirements\n"
            "• Response format specifications\n"
            "• Administrative contact details\n\n"
            "Do NOT include any information regarding:\n"
            "• Evaluation criteria\n"
            "• Project timelines or deadlines\n"
            "• Technical solution or deliverable specifications\n\n"
            "Text to analyze:\n"
            f"{text}"
        ),
        'dk': (
            "Uddrag venligst de administrative og proceduremæssige krav for indsendelse af dette udbud fra teksten nedenfor. "
            "Fokuser på elementer som:\n"
            "• Dokumentformatregler (f.eks. sidebegrænsninger, påkrævede afsnit)\n"
            "• Juridiske og licensmæssige forudsætninger\n"
            "• Indsendelsesmetoder (f.eks. hvor og hvordan der skal indsendes)\n"
            "• Påkrævede certifikater eller dokumentation\n"
            "• Forsikrings- eller garantikrav\n"
            "• Specifikationer for svarformat\n"
            "• Administrative kontaktoplysninger\n\n"
            "Medtag IKKE information om:\n"
            "• Evalueringskriterier\n"
            "• Projekt tidslinjer eller deadlines\n"
            "• Tekniske løsninger eller leverancespecifikationer\n\n"
            "Tekst til analyse:\n"
            f"{text}"
        )
    }

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_content.get(language, system_content['en'])
            },
            {
                "role": "user",
                "content": user_content.get(language, user_content['en'])
            }
        ]
    )

    try:
        content = completion.choices[0].message.content
        if content:
            return content
    except Exception:
        return ""

async def extract_solution_requirements(text: str, language: str) -> str:
    system_content = {
        'en': (
            "You are a detail-oriented analyst specializing in tender documents. "
            "Your task is to extract only the solution requirements – that is, the specific deliverables, items, functionalities, or services that must be provided. "
            "Please list each requirement as a bullet point starting with '• '. "
            "Exclude any administrative details, submission procedures, legal or licensing prerequisites, evaluation criteria, or timelines."
        ),
        'dk': (
            "Du er en detaljeorienteret analytiker specialiseret i udbudsdokumenter. "
            "Din opgave er at uddrage kun løsningskravene – det vil sige de specifikke leverancer, elementer, funktionaliteter eller tjenester, der skal leveres. "
            "Angiv venligst hvert krav som et punkt startende med '• '. "
            "Udelad administrative detaljer, indsendelsesprocedurer, juridiske eller licensmæssige forudsætninger, evalueringskriterier eller tidslinjer."
        )
    }

    user_content = {
        'en': (
            "Extract ONLY the solution requirements from the text below. "
            "Focus exclusively on what must be delivered (i.e., the specific deliverables, items, functionalities, or services required) and ignore everything else.\n\n"
            "Do NOT include any of the following:\n"
            "• Administrative requirements (e.g., page limits, formatting rules)\n"
            "• Submission procedures\n"
            "• Legal or licensing prerequisites\n"
            "• Evaluation criteria\n"
            "• Timelines or deadlines\n\n"
            "Text to analyze:\n"
            f"{text}"
        ),
        'dk': (
            "Uddrag KUN løsningskravene fra teksten nedenfor. "
            "Fokuser udelukkende på hvad der skal leveres (dvs. de specifikke leverancer, elementer, funktionaliteter eller tjenester der kræves) og ignorer alt andet.\n\n"
            "Medtag IKKE følgende:\n"
            "• Administrative krav (f.eks. sidebegrænsninger, formateringsregler)\n"
            "• Indsendelsesprocedurer\n"
            "• Juridiske eller licensmæssige forudsætninger\n"
            "• Evalueringskriterier\n"
            "• Tidsfrister eller deadlines\n\n"
            "Tekst til analyse:\n"
            f"{text}"
        )
    }

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_content.get(language, system_content['en'])
            },
            {
                "role": "user",
                "content": user_content.get(language, user_content['en'])
            }
        ]
    )

    try:
        content = completion.choices[0].message.content
        if content:
            return content
    except Exception:
        return ""

async def extract_timeline_requirements(text: str, language: str) -> str:
    system_content = {
        'en': (
            "You are a detail-oriented analyst focused on extracting timeline information from tender documents. "
            "Your task is to identify and extract every date or time period mentioned, regardless of context."
        ),
        'dk': (
            "Du er en detaljeorienteret analytiker fokuseret på at uddrage tidslinjeinformation fra udbudsdokumenter. "
            "Din opgave er at identificere og uddrage alle datoer eller tidsperioder der nævnes, uanset kontekst."
        )
    }

    user_content = {
        'en': (
            "Extract ALL tender-related dates and deadlines from the text below. Include any date or time period "
            "that could be relevant, such as:\n"
            "• Question/clarification submission deadlines\n"
            "• Proposal/bid submission deadlines\n"
            "• Contract award date\n"
            "• Project start and end dates\n"
            "• Site visit or pre-bid meeting dates\n"
            "• Bid validity period\n"
            "• Contract duration\n"
            "• Payment milestones\n"
            "• Any other mentioned dates or time periods\n\n"
            "Output each entry in the format: 'DATE/PERIOD: ACTION' (maximum of 8 words per entry). "
            "Ensure the list is sorted chronologically.\n\n"
            f"Text to analyze:\n{text}"
        ),
        'dk': (
            "Uddrag ALLE udbudsrelaterede datoer og deadlines fra teksten nedenfor. Inkluder enhver dato eller tidsperiode "
            "der kunne være relevant, såsom:\n"
            "• Spørgsmål/afklarings indsendelsesfrister\n"
            "• Tilbuds/bud indsendelsesfrister\n"
            "• Kontrakttildelingsdato\n"
            "• Projekt start- og slutdatoer\n"
            "• Besigtigelse eller før-tilbuds mødedatoer\n"
            "• Tilbuds gyldighedsperiode\n"
            "• Kontraktvarighed\n"
            "• Betalingsmilestene\n"
            "• Alle andre nævnte datoer eller tidsperioder\n\n"
            "Angiv hvert punkt i formatet: 'DATO/PERIODE: HANDLING' (maksimalt 8 ord pr. punkt). "
            "Sørg for at listen er sorteret kronologisk.\n\n"
            f"Tekst til analyse:\n{text}"
        )
    }

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_content.get(language, system_content['en'])
            },
            {
                "role": "user",
                "content": user_content.get(language, user_content['en'])
            }
        ]
    )

    try:
        content = completion.choices[0].message.content
        if content:
            return content
    except Exception:
        return ""

async def extract_award_criteria(text: str, language: str) -> str:
    system_content = {
        'en': (
            "You are a detail-oriented analyst focused on extracting award criteria. "
            "Your task is to extract ONLY the evaluation and award criteria used to score or assess proposals."
        ),
        'dk': (
            "Du er en detaljeorienteret analytiker fokuseret på at uddrage tildelingskriterier. "
            "Din opgave er at uddrage KUN evaluerings- og tildelingskriterierne der bruges til at bedømme eller vurdere tilbud."
        )
    }

    user_content = {
        'en': (
            "Extract ONLY the evaluation and award criteria from the text below. "
            "Focus on identifying:\n"
            "• Scoring weights and percentages\n"
            "• Technical evaluation criteria\n"
            "• Financial/price evaluation methods\n"
            "• Minimum qualifying scores\n"
            "• Specific scoring breakdowns\n\n"
            "Do NOT include any of the following:\n"
            "• Administrative requirements\n"
            "• Solution specifications\n"
            "• Timelines or deadlines\n"
            "• Submission procedures\n"
            "• Legal prerequisites\n\n"
            f"Text to analyze:\n{text}"
        ),
        'dk': (
            "Uddrag KUN evaluerings- og tildelingskriterierne fra teksten nedenfor. "
            "Fokuser på at identificere:\n"
            "• Vægtning og procentfordeling\n"
            "• Tekniske evalueringskriterier\n"
            "• Finansielle/prismæssige evalueringsmetoder\n"
            "• Minimumskrav til point\n"
            "• Specifikke pointfordelinger\n\n"
            "Medtag IKKE følgende:\n"
            "• Administrative krav\n"
            "• Løsningsspecifikationer\n"
            "• Tidslinjer eller deadlines\n"
            "• Indsendelsesprocedurer\n"
            "• Juridiske forudsætninger\n\n"
            f"Tekst til analyse:\n{text}"
        )
    }

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_content.get(language, system_content['en'])
            },
            {
                "role": "user",
                "content": user_content.get(language, user_content['en'])
            }
        ]
    )

    try:
        content = completion.choices[0].message.content
        return content if content else ""
    except Exception:
        return ""

async def extract_price_information(text: str, language: str) -> str:
    system_content = {
        'en': (
            "You are a detail-oriented analyst focused on extracting contract value information. "
            "Your task is to extract ONLY the estimated or actual monetary value of the contract."
        ),
        'dk': (
            "Du er en detaljeorienteret analytiker fokuseret på at uddrage kontraktværdi information. "
            "Din opgave er at uddrage KUN den estimerede eller faktiske monetære værdi af kontrakten."
        )
    }

    user_content = {
        'en': (
            "Extract ONLY the contract value information from the text below. "
            "Focus on identifying:\n"
            "• Total contract value\n"
            "• Estimated budget\n" 
            "• Price ranges\n"
            "• Lot values (if split into lots)\n"
            "• Annual values (if multi-year)\n\n"
            "Return ONLY the numerical values with their currency. "
            "If a range is given, include both the minimum and maximum.\n\n"
            f"Text to analyze:\n{text}"
        ),
        'dk': (
            "Uddrag KUN information om kontraktværdien fra teksten nedenfor. "
            "Fokuser på at identificere:\n"
            "• Total kontraktværdi\n"
            "• Estimeret budget\n"
            "• Prisintervaller\n"
            "• Delkontrakt-værdier (hvis opdelt i delkontrakter)\n"
            "• Årlige værdier (hvis flerårig)\n\n"
            "Returner KUN de numeriske værdier med deres valuta. "
            "Hvis der er angivet et interval, inkluder både minimum og maksimum.\n\n"
            f"Tekst til analyse:\n{text}"
        )
    }

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_content.get(language, system_content['en'])
            },
            {
                "role": "user", 
                "content": user_content.get(language, user_content['en'])
            }
        ]
    )

    try:
        content = completion.choices[0].message.content
        return content if content else ""
    except Exception:
        return ""