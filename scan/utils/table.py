# ============================================================================
# FILE: scan/utils/table.py - SMART TABLE DETECTION
# ============================================================================

import re


def detect_table_candidates(raw_text: str) -> dict:
    """
    Analyzes raw OCR text to detect content that should be presented as tables.
    Returns a dict with table hints for the AI prompt.
    
    Strategy: Only suggest tables when they REDUCE cognitive load and save space.
    Not every list should be a table - only when grouping provides clear value.
    """
    
    table_hints = {
        'has_tables': False,
        'table_topics': [],
        'table_keywords': [],
        'suggestion': ''
    }
    
    # Convert to lowercase for analysis
    text_lower = raw_text.lower()
    
    # ===== PATTERN 1: Explicit categorization keywords =====
    # These almost always benefit from tables
    strong_table_indicators = [
        r'types of\s+\w+',
        r'kinds of\s+\w+',
        r'categories of\s+\w+',
        r'classification of\s+\w+',
        r'branches of\s+\w+',
        r'divisions of\s+\w+',
        r'classes of\s+\w+',
        r'forms of\s+\w+',
        r'stages of\s+\w+',
        r'phases of\s+\w+',
        r'levels of\s+\w+',
    ]
    
    for pattern in strong_table_indicators:
        matches = re.findall(pattern, text_lower)
        if matches:
            table_hints['has_tables'] = True
            for match in matches:
                # Extract the topic (e.g., "types of rocks" -> "rocks")
                topic = match.split('of')[-1].strip()
                if topic not in table_hints['table_topics']:
                    table_hints['table_topics'].append(match)
                    table_hints['table_keywords'].append(topic)
    
    # ===== PATTERN 2: Comparative structures =====
    # "A vs B", "compared to", "differences between"
    comparison_patterns = [
        r'(\w+)\s+vs\.?\s+(\w+)',
        r'(\w+)\s+versus\s+(\w+)',
        r'difference[s]?\s+between\s+(\w+)\s+and\s+(\w+)',
        r'compar(e|ing|ison)\s+(\w+)\s+(and|with)\s+(\w+)',
    ]
    
    for pattern in comparison_patterns:
        matches = re.findall(pattern, text_lower)
        if matches and len(matches) >= 2:  # Need at least 2 comparisons
            table_hints['has_tables'] = True
            table_hints['table_topics'].append('comparison table')
    
    # ===== PATTERN 3: Structured lists with attributes =====
    # Example: "Bacteria: causes disease, found in...\nVirus: causes..."
    # Look for repeated colon patterns with similar structure
    colon_lines = [line for line in raw_text.split('\n') if ':' in line and len(line) < 200]
    if len(colon_lines) >= 3:  # At least 3 similar structured lines
        # Check if they follow similar pattern (Item: description)
        structured_count = sum(1 for line in colon_lines if re.match(r'^\w+[\w\s]*:', line.strip()))
        if structured_count >= 3:
            table_hints['has_tables'] = True
            table_hints['table_topics'].append('structured list')
    
    # ===== PATTERN 4: Enumerated properties =====
    # "Properties of X: 1. ... 2. ... 3. ..."
    # "Characteristics of X: a) ... b) ... c) ..."
    if re.search(r'(properties|characteristics|features|attributes)\s+of\s+\w+', text_lower):
        # Count numbered/lettered items
        numbered_items = len(re.findall(r'^\s*[\d\w][\.)]\s+', raw_text, re.MULTILINE))
        if numbered_items >= 4:  # 4+ enumerated items
            table_hints['has_tables'] = True
            table_hints['table_topics'].append('properties table')
    
    # ===== PATTERN 5: Matrix-like content =====
    # Multiple entities with multiple shared attributes
    # Example: "Disease X: caused by... transmitted by... treated with..."
    #          "Disease Y: caused by... transmitted by... treated with..."
    
    # Look for repeated attribute keywords across multiple subjects
    attribute_keywords = ['caused by', 'transmitted', 'treated', 'prevented', 'symptoms', 
                         'example', 'definition', 'formula', 'purpose', 'function']
    
    attribute_counts = {}
    for keyword in attribute_keywords:
        count = len(re.findall(keyword, text_lower))
        if count >= 3:  # Same attribute mentioned 3+ times
            attribute_counts[keyword] = count
    
    if len(attribute_counts) >= 2:  # 2+ attributes repeated across items
        table_hints['has_tables'] = True
        table_hints['table_topics'].append('attribute matrix')
    
    # ===== BUILD SUGGESTION FOR AI =====
    if table_hints['has_tables']:
        unique_topics = list(set(table_hints['table_topics']))
        
        if len(unique_topics) == 1:
            table_hints['suggestion'] = f"This content contains {unique_topics[0]}. Present it as a table with NO Explanation or Example fields."
        elif len(unique_topics) <= 3:
            topics_str = ', '.join(unique_topics)
            table_hints['suggestion'] = f"This content contains: {topics_str}. Present these as tables with NO Explanation or Example fields."
        else:
            table_hints['suggestion'] = "This content has multiple categorized sections. Present them as tables where appropriate, with NO Explanation or Example fields for table answers."
    
    return table_hints


def should_use_table(text_chunk: str, min_items: int = 3, max_items: int = 10) -> bool:
    """
    Quick check: Should this specific text chunk be a table?
    
    Args:
        text_chunk: A section of text (e.g., one question's worth)
        min_items: Minimum number of items to justify a table (default: 3)
        max_items: Maximum items to keep tables concise (default: 10)
    
    Returns:
        bool: True if table format is beneficial
    """
    
    # Count potential table rows
    # Look for patterns like bullet points, numbered lists, or colon-separated items
    
    patterns = [
        r'^\s*[-•*]\s+',  # Bullet points
        r'^\s*\d+[\.)]\s+',  # Numbered lists
        r'^\w+[\w\s]*:\s*\w+',  # Key: value pairs
    ]
    
    item_count = 0
    for pattern in patterns:
        matches = re.findall(pattern, text_chunk, re.MULTILINE)
        item_count = max(item_count, len(matches))
    
    # Also check for table-like structure (rows with similar format)
    lines = [l.strip() for l in text_chunk.split('\n') if l.strip()]
    if len(lines) >= min_items:
        # Check if lines have similar structure (e.g., all have colons)
        colon_lines = sum(1 for line in lines if ':' in line)
        if colon_lines >= min_items:
            item_count = colon_lines
    
    # Use table only if:
    # 1. We have enough items (min_items)
    # 2. Not too many items (max_items) - long tables are hard to read
    # 3. Items have similar structure
    
    return min_items <= item_count <= max_items


def count_table_potential_items(text: str) -> int:
    """
    Count how many items could potentially be table rows.
    Used to prevent creating tables with too few or too many rows.
    """
    
    # Count items from various patterns
    bullet_count = len(re.findall(r'^\s*[-•*]\s+', text, re.MULTILINE))
    number_count = len(re.findall(r'^\s*\d+[\.)]\s+', text, re.MULTILINE))
    colon_count = len(re.findall(r'^\w+[\w\s]*:\s*\w+', text, re.MULTILINE))
    
    return max(bullet_count, number_count, colon_count)


def extract_table_keywords(text: str) -> list:
    """
    Extract specific keywords that suggest table content.
    Returns list of topics that should be tables.
    
    Example: "types of bacteria" -> ["bacteria"]
    """
    
    keywords = []
    
    patterns = [
        (r'types of\s+(\w+)', 1),
        (r'kinds of\s+(\w+)', 1),
        (r'categories of\s+(\w+)', 1),
        (r'branches of\s+(\w+)', 1),
        (r'classification of\s+(\w+)', 1),
    ]
    
    for pattern, group in patterns:
        matches = re.findall(pattern, text.lower())
        keywords.extend(matches)
    
    return list(set(keywords))  # Remove duplicates


def generate_table_instruction(table_hints: dict, difficulty_level: str = 'medium') -> str:
    """
    Generate specific instruction to add to AI prompt based on detected tables.
    
    Args:
        table_hints: Output from detect_table_candidates()
        difficulty_level: 'easy', 'medium', or 'difficult'
    
    Returns:
        str: Instruction text to append to AI prompt
    """
    
    if not table_hints['has_tables']:
        return ""
    
    instruction = "\n\n═══════════════════════════════════════════════════════════════════\n"
    instruction += "⚠️ TABLE DETECTION - SPECIAL INSTRUCTIONS\n"
    instruction += "═══════════════════════════════════════════════════════════════════\n\n"
    
    instruction += table_hints['suggestion'] + "\n\n"
    
    if table_hints['table_keywords']:
        keywords_str = ', '.join(table_hints['table_keywords'][:3])  # Show max 3 examples
        instruction += f"Detected table topics: {keywords_str}\n\n"
    
    instruction += "TABLE RULES:\n"
    instruction += "• ONLY use tables when content has 3-10 similar items\n"
    instruction += "• Table answers get NO Explanation field\n"
    instruction += "• Table answers get NO Example field\n"
    instruction += "• Only: Question + Answer (as table) + Separator (---)\n"
    instruction += "• Keep tables concise - max 10 rows\n"
    instruction += "• If content has 10+ items, split into 2 questions with 2 tables\n\n"
    
    instruction += "═══════════════════════════════════════════════════════════════════\n"
    
    return instruction
