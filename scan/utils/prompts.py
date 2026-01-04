# ============================================================================
# FILE: scan/utils/prompts.py - DIFFICULTY-SPECIFIC PROMPT TEMPLATES
# ============================================================================

from .table import detect_table_candidates, generate_table_instruction


def get_easy_prompt(topic_title: str, raw_text: str) -> str:
    """
    EASY LEVEL: Quick recognition, basic facts, simple local references
    Cognitive Goal: Student can RECOGNIZE concept
    """
    
    # Detect if content should have tables
    table_hints = detect_table_candidates(raw_text)
    
    base_prompt = f"""You are creating EASY-LEVEL study flashcards for community college students in Monrovia, Liberia.

EASY LEVEL GOAL: Help students RECOGNIZE and REMEMBER concepts quickly.

Topic: {topic_title}

OCR TEXT:
{raw_text}

═══════════════════════════════════════════════════════════════════
EASY LEVEL REQUIREMENTS
═══════════════════════════════════════════════════════════════════

Answer: 4-6 words MAXIMUM
Explanation: STATE THE BASIC FACT (6-8 words) - What is it? What does it do?
Example: SIMPLE LOCAL REFERENCE (5-7 words) - Generic Liberia/West Africa mention

FORBIDDEN:
❌ No complex mechanisms or processes
❌ No "because...which...that" chains
❌ Keep it surface-level and clear

═══════════════════════════════════════════════════════════════════
PERFECT EASY EXAMPLES
═══════════════════════════════════════════════════════════════════

Q1: What causes malaria transmission?
Answer: Infected female Anopheles mosquito bite

Explanation: Parasite enters bloodstream and infects red cells

Example: Monrovia rainy season increases mosquito breeding

---

Q2: What is petty trading?
Answer: Selling small goods for quick profit

Explanation: Low investment generates daily income for survival

Example: Waterside Market women sell rice cups

---

Q3: What is due process?
Answer: Fair legal procedures protect accused rights

Explanation: Courts must follow rules before convicting anyone

Example: Monrovia Magistrate Court requires lawyer access

---

Q4: What is crop rotation?
Answer: Planting different crops each season

Explanation: Prevents soil depletion and reduces pests

Example: Cassava then rice prevents soil exhaustion

---

Q5: What is formative assessment?
Answer: Ongoing checks during learning process

Explanation: Teachers adjust instruction based on student progress

Example: WASSCE mock exams identify weak areas

---

═══════════════════════════════════════════════════════════════════
LOCAL CONTEXT BANK - USE IN EXAMPLES
═══════════════════════════════════════════════════════════════════

HEALTH: malaria, cholera, Ebola, JFK Hospital, ELWA Hospital, rainy season
BUSINESS: Waterside Market, Red Light Market, petty trading, mobile money
JUSTICE: Monrovia Magistrate Court, Temple of Justice, Liberian National Police
AGRICULTURE: cassava, rubber, rice paddies, palm oil
EDUCATION: University of Liberia, WASSCE exams, Tubman University
GEOGRAPHY: Montserrado County, Monrovia, Paynesville, West Africa

═══════════════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════════════

1. Read ALL OCR text
2. Create 15-20 questions covering all important material
3. For EACH question:
   • Clear question
   • Answer (4-6 words)
   • Explanation: Basic fact (6-8 words)
   • Example: Simple local reference (5-7 words)
   • Separator (---)

4. EXCEPTION for tables: Q + Answer (table) + --- (NO Explanation/Example)

FORMAT:

Q1: [Question]
Answer: [4-6 words]

Explanation: [Basic fact - 6-8 words]

Example: [Simple reference - 5-7 words]

---

Begin now:"""

    # Add table-specific instruction if detected
    if table_hints['has_tables']:
        table_instruction = generate_table_instruction(table_hints, 'easy')
        base_prompt += "\n" + table_instruction
    
    return base_prompt


def get_medium_prompt(topic_title: str, raw_text: str) -> str:
    """
    MEDIUM LEVEL: Show mechanisms, specific context, concrete details
    Cognitive Goal: Student can UNDERSTAND and EXPLAIN concept
    """
    
    # Detect if content should have tables
    table_hints = detect_table_candidates(raw_text)
    
    base_prompt = f"""You are creating MEDIUM-LEVEL study flashcards for community college students in Monrovia, Liberia.

MEDIUM LEVEL GOAL: Help students UNDERSTAND and EXPLAIN concepts.

Topic: {topic_title}

OCR TEXT:
{raw_text}

═══════════════════════════════════════════════════════════════════
MEDIUM LEVEL REQUIREMENTS
═══════════════════════════════════════════════════════════════════

Answer: 4-6 words MAXIMUM (same as Easy)
Explanation: EXPLAIN THE MECHANISM (8-12 words) - WHY does this happen? HOW does it work?
Example: SPECIFIC LOCATION + CONCRETE DETAILS (7-10 words)

FOCUS ON:
✓ Show WHY or HOW something works
✓ Reveal the mechanism simply
✓ Use specific places and concrete details

═══════════════════════════════════════════════════════════════════
PERFECT MEDIUM EXAMPLES
═══════════════════════════════════════════════════════════════════

Q1: What causes malaria transmission?
Answer: Infected female Anopheles mosquito bite

Explanation: Mosquito transfers Plasmodium parasite when biting; parasite multiplies in blood cells

Example: Standing water near Waterside Market creates breeding sites during June-September rains

---

Q2: What is petty trading?
Answer: Selling small goods for quick profit

Explanation: Traders buy small quantities wholesale, then resell in smaller portions at slight markup for immediate cash

Example: Woman buys 50kg rice bag for $25, sells cups for $0.50 each, earns $10 daily profit

---

Q3: What is due process?
Answer: Fair legal procedures protect accused rights

Explanation: Government must respect legal rights and follow established procedures before punishment

Example: Police arrest suspect in Paynesville; must bring before magistrate within 48 hours or release

---

Q4: What is crop rotation?
Answer: Planting different crops each season

Explanation: Each crop takes different nutrients; rotating lets soil recover naturally

Example: Bong County farmers plant cassava, then rice, then beans

---

Q5: What is formative assessment?
Answer: Ongoing checks during learning process

Explanation: Teachers adjust teaching methods based on student understanding and progress

Example: University of Liberia professors use weekly quizzes to identify struggling students

---

═══════════════════════════════════════════════════════════════════
LOCAL CONTEXT BANK - USE SPECIFIC DETAILS
═══════════════════════════════════════════════════════════════════

HEALTH: JFK Hospital Monrovia, ELWA Hospital, June-September rainy season, oral rehydration
BUSINESS: Waterside Market daily trading, Red Light Market wholesale, Orange Money, market queens
JUSTICE: Monrovia Central Prison, Temple of Justice, LNP procedures, 48-hour detention
AGRICULTURE: Bong County rubber plantations, Nimba County rice paddies, palm oil extraction
EDUCATION: University of Liberia Fendall Campus, WASSCE May/June exams
GEOGRAPHY: Montserrado County coastal areas, Bushrod Island, Paynesville suburbs

═══════════════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════════════

1. Read ALL OCR text
2. Create 15-20 questions covering all important material
3. For EACH question:
   • Clear question
   • Answer (4-6 words)
   • Explanation: Show mechanism WHY/HOW (8-12 words)
   • Example: Specific place + concrete details (7-10 words)
   • Separator (---)

4. EXCEPTION for tables: Q + Answer (table) + --- (NO Explanation/Example)

QUALITY CHECK:
- Does explanation show WHY or HOW?
- Does example include specific location + concrete detail?

FORMAT:

Q1: [Question]
Answer: [4-6 words]

Explanation: [Mechanism - WHY/HOW - 8-12 words]

Example: [Specific place + details - 7-10 words]

---

Begin now:"""

    # Add table-specific instruction if detected
    if table_hints['has_tables']:
        table_instruction = generate_table_instruction(table_hints, 'medium')
        base_prompt += "\n" + table_instruction
    
    return base_prompt


def get_difficult_prompt(topic_title: str, raw_text: str) -> str:
    """
    DIFFICULT LEVEL: Complete cause-and-effect, rich scenarios, deep context
    Cognitive Goal: Student can APPLY and USE concept in new situations
    """
    
    # Detect if content should have tables
    table_hints = detect_table_candidates(raw_text)
    
    base_prompt = f"""You are creating DIFFICULT-LEVEL study flashcards for community college students in Monrovia, Liberia.

DIFFICULT LEVEL GOAL: Help students MASTER and APPLY concepts.

Topic: {topic_title}

OCR TEXT:
{raw_text}

═══════════════════════════════════════════════════════════════════
DIFFICULT LEVEL REQUIREMENTS
═══════════════════════════════════════════════════════════════════

Answer: 4-6 words MAXIMUM (same as Easy/Medium)
Explanation: COMPLETE CAUSE-AND-EFFECT (10-15 words) - Full process/relationship
Example: REAL-WORLD SCENARIO (10-15 words) - Mini-story showing principle

FOCUS ON:
✓ Show complete process and relationships
✓ Reveal cause-and-effect chains clearly
✓ Create realistic scenarios demonstrating principle

═══════════════════════════════════════════════════════════════════
PERFECT DIFFICULT EXAMPLES
═══════════════════════════════════════════════════════════════════

Q1: What causes malaria transmission?
Answer: Infected female Anopheles mosquito bite

Explanation: Female mosquito needs blood for eggs; if previous host had malaria, she carries Plasmodium which enters new host's bloodstream where it reproduces in liver then red blood cells

Example: Family living near swamp in Paynesville: father gets malaria, mosquitoes bite him then bite children at night, whole family infected within two weeks

---

Q2: What is petty trading?
Answer: Selling small goods for quick profit

Explanation: Informal economy survival strategy where traders use minimal capital to buy wholesale, break into affordable portions for poor customers, and generate daily cash flow despite slim margins

Example: Widow at Duala Market: borrows $20 from savings club, buys bulk oil and sugar, divides into small bags, sells all day at tiny markup, repays loan plus interest, feeds children with remainder - repeats daily

---

Q3: What is due process?
Answer: Fair legal procedures protect accused rights

Explanation: Prevents government abuse by requiring proper notice, fair hearing, legal representation, and evidence presentation before any punishment

Example: Man accused of theft at Red Light Market: police must explain charges, allow him to hire lawyer, present evidence in court, and let him challenge witnesses before judge can rule

---

Q4: What is crop rotation?
Answer: Planting different crops each season

Explanation: Different crops extract different nutrients; rotation prevents depletion while some crops actually replenish what others removed

Example: After cassava depletes nitrogen, farmers plant legumes like peanuts which restore nitrogen naturally before next rice season

---

Q5: What is formative assessment?
Answer: Ongoing checks during learning process

Explanation: Teachers continuously evaluate student understanding throughout semester to identify gaps, adjust teaching strategies, and provide targeted help before final exams

Example: Tubman University professor notices students struggling with statistics: adds extra workshop sessions, creates study groups, provides practice problems, resulting in 40% grade improvement by midterm

---

═══════════════════════════════════════════════════════════════════
LOCAL CONTEXT BANK - CREATE RICH SCENARIOS
═══════════════════════════════════════════════════════════════════

HEALTH: JFK Hospital emergency, ELWA maternity ward, cholera treatment centers, malaria prevention
BUSINESS: Waterside savings clubs (susu), Red Light wholesale suppliers, mobile money agents, market queen disputes
JUSTICE: Temple of Justice proceedings, Monrovia Central Prison, LNP investigations, legal aid clinics
AGRICULTURE: Bong County rubber cooperatives, Nimba rice cycles, palm oil plantations, rainy season storage
EDUCATION: University of Liberia enrollment, WASSCE preparation, scholarship applications, peer tutoring
GEOGRAPHY: Montserrado flood zones, Bushrod Island markets, Paynesville urbanization, Atlantic coast fishing

═══════════════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════════════

1. Read ALL OCR text
2. Create 15-20 questions covering all important material
3. For EACH question:
   • Clear question
   • Answer (4-6 words)
   • Explanation: Complete cause-and-effect (10-15 words)
   • Example: Real-world scenario (10-15 words)
   • Separator (---)

4. EXCEPTION for tables: Q + Answer (table) + --- (NO Explanation/Example)

QUALITY CHECK:
- Does explanation show complete process?
- Does example create mini-story showing principle?

FORMAT:

Q1: [Question]
Answer: [4-6 words]

Explanation: [Complete cause-and-effect - 10-15 words]

Example: [Real scenario - 10-15 words]

---

Begin now:"""

    # Add table-specific instruction if detected
    if table_hints['has_tables']:
        table_instruction = generate_table_instruction(table_hints, 'difficult')
        base_prompt += "\n" + table_instruction
    
    return base_prompt