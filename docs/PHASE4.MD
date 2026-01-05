# Phase 4: Dynamic Difficulty System

## Overview
Phase 4 introduces user-controlled difficulty levels for AI-generated content, allowing learners to choose how deep they want to study each topic—from quick recognition (Easy) to exam mastery (Difficult).

---

## The Problem We're Solving

### Before Phase 4:
- ❌ One-size-fits-all AI generation
- ❌ Can't adjust depth per topic
- ❌ Students stuck with medium difficulty
- ❌ No flexibility for different learning goals
- ❌ Difficulty set at topic creation (unchangeable)

### After Phase 4:
- ✅ Three difficulty levels (Easy, Medium, Difficult)
- ✅ User selects difficulty when generating
- ✅ Can regenerate same topic at different levels
- ✅ Difficulty choice persists per generation
- ✅ Different explanations for same content
- ✅ Flexible learning paths

---

## Core Design Principles

### 1️⃣ Three Distinct Difficulty Levels

**⚡ Easy - Quick Recognition**
- **Purpose**: Fast review, habit building
- **Answer**: 4-6 words (basic facts only)
- **Explanation**: 6-8 words (simple "what")
- **Example**: 5-7 words (straightforward scenario)
- **Best for**: Daily reviews, memorization, exam prep cramming

**📚 Medium - Understanding**
- **Purpose**: Conceptual understanding
- **Answer**: 4-6 words (key concept)
- **Explanation**: 6-8 words (WHY/HOW it works)
- **Example**: 5-7 words (specific local context)
- **Best for**: Regular study, learning new material, comprehension

**🎓 Difficult - Mastery**
- **Purpose**: Deep learning, exam excellence
- **Answer**: 4-6 words (precise definition)
- **Explanation**: 6-8 words (cause-and-effect mechanisms)
- **Example**: 5-7 words (real-world Liberian scenario)
- **Best for**: Exam preparation, thesis work, teaching others

---

### 2️⃣ User-Controlled Generation

**Key Principle**: Difficulty is selected *when generating*, not when creating the topic.

**Workflow**:
```
1. Admin creates topic (no difficulty choice yet)
2. Admin navigates to AI Refine Comparison page
3. Admin selects difficulty level (Easy/Medium/Difficult)
4. Admin clicks generate (Gemini/Groq/Both)
5. AI generates at selected difficulty
6. Difficulty is saved to Topic model
7. Admin can change and regenerate anytime
```

---

## Part A: Database Changes

### Topic Model Update

**New Field**: `difficulty_level`

```python
class Topic(BaseModel):
    # ... existing fields ...
    
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy - Quick Recognition'),
            ('medium', 'Medium - Understanding'),
            ('difficult', 'Difficult - Mastery'),
        ],
        default='medium',
        help_text="Determines explanation depth for AI generation"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['difficulty_level']),
        ]
```

**Migration**:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### AIRefine Model Update

**New Field**: `difficulty_level`

```python
class AIRefine(BaseModel):
    # ... existing fields ...
    
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('difficult', 'Difficult'),
        ],
        default='medium',
        help_text="Difficulty level used for this refinement"
    )
    
    class Meta:
        unique_together = ['topic', 'provider', 'difficulty_level']
```

**Why unique_together?** Each topic can have multiple AI refines per provider (one per difficulty level).

---

## Part B: Frontend Changes

### AI Refine Comparison Page

**Template**: `scan/templates/scan/partials/ai_refine.html`

**Key Additions**:

1. **Dynamic Difficulty Indicator** (updates in real-time)
2. **Difficulty Selection Radio Buttons** (3 options)
3. **JavaScript to sync selection with indicator**
4. **POST difficulty with generation request**

**JavaScript Function**:
```javascript
function updateDifficultyDisplay(level) {
    // Updates top indicator when radio button changes
    // Shows appropriate emoji and description
    // Changes colors (green/yellow/red)
}

async function generateAIRefines(provider) {
    // Gets selected difficulty from radio buttons
    // Sends difficulty in POST request
    // Updates loading message with difficulty
}
```

---

### Text Input Pages (Removed Difficulty)

**Changed**: `text_input.html`, `save_topic.html`

**Before**: Had difficulty selection during topic creation

**After**: Removed—difficulty is now selected when generating AI refines

**Rationale**: Separating content creation from AI generation gives more flexibility

---

## Part C: Backend Changes

### Views Update

**File**: `scan/ai_views.py`

**Key Changes**:

1. **Accept difficulty from POST request**:
```python
def generate_ai_refine(request, topic_id):
    difficulty = request.POST.get('difficulty', 'medium')
```

2. **Save difficulty to Topic**:
```python
topic.difficulty_level = difficulty
topic.save(update_fields=['difficulty_level', 'updated_at'])
```

3. **Pass difficulty to AI functions**:
```python
refined_text, time, count = refine_with_gemini(
    topic.raw_text,
    topic.title,
    difficulty_level=difficulty  # ← Pass selected difficulty
)
```

4. **Store difficulty in AIRefine**:
```python
AIRefine.objects.get_or_create(
    topic=topic,
    provider='gemini',
    difficulty_level=difficulty,  # ← Track which difficulty was used
    defaults={'status': 'processing'}
)
```

---

### AI Prompt Engineering

**File**: `scan/utils/ai.py`

**Function**: `refine_with_gemini()`, `refine_with_groq()`

**Difficulty-Specific Prompts**:

```python
def get_difficulty_prompt(difficulty_level):
    """Returns tailored instructions based on difficulty"""
    
    if difficulty_level == 'easy':
        return """
        EASY LEVEL - Quick Recognition:
        - Answer: Simple, direct facts only
        - Explanation: Basic "what" - no mechanisms
        - Example: Straightforward scenario
        - Goal: Fast review and memorization
        
        Example:
        Q: What causes malaria?
        Answer: Infected mosquito bite
        Explanation: Mosquito transmits parasite to humans
        Example: Rainy season increases mosquito bites
        """
    
    elif difficulty_level == 'medium':
        return """
        MEDIUM LEVEL - Understanding:
        - Answer: Key concept
        - Explanation: WHY/HOW it works
        - Example: Specific local context
        - Goal: Conceptual understanding
        
        Example:
        Q: What causes malaria?
        Answer: Infected female Anopheles mosquito bite
        Explanation: Parasite enters bloodstream and infects red cells
        Example: Monrovia rainy season increases mosquito breeding
        """
    
    else:  # difficult
        return """
        DIFFICULT LEVEL - Mastery:
        - Answer: Precise, complete definition
        - Explanation: Cause-and-effect mechanisms with full context
        - Example: Real-world Liberian scenario with implications
        - Goal: Exam mastery and deep understanding
        
        Example:
        Q: What causes malaria?
        Answer: Plasmodium parasite via infected Anopheles bite
        Explanation: Female mosquito injects sporozoites that infect liver cells
        Example: JFK Hospital treats severe cerebral malaria cases
        """
```

**Implementation**:
```python
def refine_with_gemini(raw_text, topic_title, difficulty_level='medium'):
    # Get difficulty-specific prompt
    diff_prompt = get_difficulty_prompt(difficulty_level)
    
    # Construct full prompt
    prompt = f"""
    {diff_prompt}
    
    [Rest of standard formatting rules...]
    
    Topic: {topic_title}
    Text: {raw_text}
    """
    
    # Call Gemini API...
```

---

## Part D: User Experience Flow

### Typical Workflow

**Scenario**: Admin wants to create study materials at different difficulty levels

```
1. CREATE TOPIC
   ├─ Upload image OR paste text
   ├─ Set title, course, page range
   └─ No difficulty selection yet ✅

2. VIEW AI REFINE PAGE
   ├─ See current difficulty (default: Medium)
   ├─ Three radio buttons: Easy | Medium | Difficult
   └─ Instructions explaining each level

3. SELECT DIFFICULTY
   ├─ Click "Easy" → Top indicator updates to green ⚡
   ├─ Click "Medium" → Top indicator updates to yellow 📚
   └─ Click "Difficult" → Top indicator updates to red 🎓

4. GENERATE
   ├─ Click "Gemini Only" or "Groq Only" or "Both"
   ├─ Loading shows: "Generating Easy level with Gemini..."
   └─ AI generates with selected difficulty

5. REVIEW & SELECT
   ├─ Compare Gemini vs Groq results
   ├─ Choose best version
   └─ Save to topic.refined_summary

6. REGENERATE (OPTIONAL)
   ├─ Change difficulty to "Difficult"
   ├─ Click "Regenerate"
   └─ Get new version at different depth
```

---

### Study Mode Integration

**Frontend (React PWA)** receives `refined_summary` with difficulty context:

```json
{
  "topic_id": 5,
  "title": "Malaria Transmission",
  "difficulty_level": "medium",
  "refined_summary": "Q1: What causes malaria?\nAnswer: Infected female Anopheles mosquito bite\n\nExplanation: Parasite enters bloodstream and infects red cells\n\nExample: Monrovia rainy season increases mosquito breeding\n\n---"
}
```

**Display**:
- Show difficulty badge (⚡📚🎓)
- Parse Q&A as usual
- Progressive disclosure (Q → A → E → Ex)

---

## Part E: AI Generation Examples

### Same Topic, Three Difficulties

**Topic**: "Photosynthesis"

**⚡ Easy**:
```
Q1: What is photosynthesis?
Answer: Plants making food from sunlight

Explanation: Leaves use light to create sugar

Example: Cassava plants grow in sunlight

---
```

**📚 Medium**:
```
Q1: What is photosynthesis?
Answer: Plants convert light into chemical energy

Explanation: Chlorophyll captures sunlight to produce glucose energy

Example: Rubber trees need sunlight for growth

---
```

**🎓 Difficult**:
```
Q1: What is photosynthesis?
Answer: Light-dependent reactions produce ATP and NADPH

Explanation: Chloroplasts use photons to split water molecules

Example: Liberian cocoa farms optimize sun exposure

---
```

---

## Part F: Quality Assurance

### Validation Checks

**Ensure difficulty prompt worked**:
```python
def validate_difficulty_compliance(refined_text, difficulty_level):
    """Check if output matches difficulty expectations"""
    
    violations = []
    
    if difficulty_level == 'easy':
        # Should use simpler language
        complex_words = ['mechanisms', 'systematic', 'comprehensive']
        for word in complex_words:
            if word.lower() in refined_text.lower():
                violations.append(f"Too complex for Easy: '{word}'")
    
    elif difficulty_level == 'difficult':
        # Should have technical terms
        if 'mechanism' not in refined_text.lower():
            violations.append("Difficult level should explain mechanisms")
    
    return violations
```

---

### Testing Different Difficulties

**Manual Test**:
1. Create test topic with simple text
2. Generate Easy → Verify simple language
3. Regenerate Medium → Verify more detail
4. Regenerate Difficult → Verify technical depth
5. Compare all three versions

**Expected Differences**:
- Easy: Basic facts, simple words
- Medium: Explanations with context
- Difficult: Technical terms, full mechanisms

---

## Part G: Admin Interface

### Difficulty Management

**Topic List View**:
- Show difficulty badge next to each topic
- Filter by difficulty level
- Bulk regenerate at different difficulty

**Topic Detail**:
- Display current difficulty
- "Change Difficulty" button → redirects to AI Refine page
- History of generated difficulties

---

## Key Achievements

1. ✅ **User-Controlled Difficulty** - Choose depth per generation
2. ✅ **Three Clear Levels** - Easy, Medium, Difficult
3. ✅ **Flexible Regeneration** - Change difficulty anytime
4. ✅ **Persistent Storage** - Difficulty saved to database
5. ✅ **AI Prompt Engineering** - Different prompts per level
6. ✅ **Real-Time UI Updates** - JavaScript syncs selection
7. ✅ **Multiple Versions** - Store Easy, Medium, Difficult separately

---

## Summary

Phase 4 adds **learning flexibility** by:

- **Letting users choose difficulty** when generating
- **Supporting three distinct levels** (Easy/Medium/Difficult)
- **Enabling regeneration** at different depths
- **Persisting difficulty choice** in database
- **Engineering AI prompts** for each level
- **Removing difficulty from topic creation** (better UX)

**Result**: Students can study the same topic at different depths based on their current learning goals—quick review before exams (Easy), conceptual learning (Medium), or deep mastery (Difficult).

---

**Phase 4 Complete! 🎉**

Learners now control how deep they dive into each topic.