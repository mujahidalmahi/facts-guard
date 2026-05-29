import re


def contains_sql_injection_pattern(text: str) -> bool:
    dangerous_patterns = [
        r"(?i)(union.*select|select.*from|drop\s+table|delete\s+from)",
        r"(?i)(exec\s*\(|execute\s*\()",
        r"(?i)(into\s+outfile|into\s+dumpfile)",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, text):
            return True

    return False
