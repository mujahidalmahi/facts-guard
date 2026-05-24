"""
Validation utilities for FactGuard backend.
Provides input validation and sanitization functions.
"""

import re
from typing import Optional
from app.exceptions import ValidationError


def validate_claim_text(claim: str) -> str:
    """
    Validate and sanitize claim text.

    Args:
        claim: The claim text to validate

    Returns:
        Sanitized claim text

    Raises:
        ValidationError: If claim is invalid
    """
    if not claim or not isinstance(claim, str):
        raise ValidationError("Claim must be a non-empty string")

    # Strip whitespace
    claim = claim.strip()

    # Check length
    if len(claim) < 5:
        raise ValidationError(
            "Claim must be at least 5 characters long",
            {"min_length": 5, "provided_length": len(claim)},
        )

    if len(claim) > 2000:
        raise ValidationError(
            "Claim must not exceed 2000 characters",
            {"max_length": 2000, "provided_length": len(claim)},
        )

    # Check for malicious patterns
    if contains_sql_injection_pattern(claim):
        raise ValidationError("Claim contains invalid characters or patterns")

    return claim


def validate_job_id(job_id: str) -> str:
    """
    Validate job ID format (UUID).

    Args:
        job_id: The job ID to validate

    Returns:
        Validated job ID

    Raises:
        ValidationError: If job_id is invalid format
    """
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

    if not re.match(uuid_pattern, job_id, re.IGNORECASE):
        raise ValidationError(
            "Invalid job ID format",
            {"expected_format": "UUID v4", "provided": job_id},
        )

    return job_id


def contains_sql_injection_pattern(text: str) -> bool:
    """
    Basic check for common SQL injection patterns.

    Args:
        text: Text to check

    Returns:
        True if potentially dangerous pattern detected

    Note:
        This is a simple check. Production systems should use
        parameterized queries which the ORM already provides.
    """
    dangerous_patterns = [
        r"(?i)(union.*select|select.*from|drop\s+table|delete\s+from)",
        r"(?i)(exec\s*\(|execute\s*\()",
        r"(?i)(into\s+outfile|into\s+dumpfile)",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, text):
            return True

    return False


def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    Sanitize string for safe storage and display.

    Args:
        text: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0]

    return text


def validate_verdict(verdict: str) -> bool:
    """
    Validate verdict value.

    Args:
        verdict: Verdict to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If verdict is invalid
    """
    valid_verdicts = {
        "Verified",
        "Likely True",
        "Mixed Evidence",
        "Likely Misleading",
        "Unverified",
    }

    if verdict not in valid_verdicts:
        raise ValidationError(
            f"Invalid verdict: {verdict}",
            {"valid_values": list(valid_verdicts), "provided": verdict},
        )

    return True


def validate_confidence(confidence: str) -> bool:
    """
    Validate confidence level.

    Args:
        confidence: Confidence level to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If confidence is invalid
    """
    valid_confidences = {"Low", "Medium", "High"}

    if confidence not in valid_confidences:
        raise ValidationError(
            f"Invalid confidence level: {confidence}",
            {
                "valid_values": list(valid_confidences),
                "provided": confidence,
            },
        )

    return True


def validate_stance(stance: str) -> bool:
    """
    Validate source stance value.

    Args:
        stance: Stance to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If stance is invalid
    """
    valid_stances = {"supports", "contradicts", "neutral"}

    if stance.lower() not in valid_stances:
        raise ValidationError(
            f"Invalid stance: {stance}",
            {"valid_values": list(valid_stances), "provided": stance},
        )

    return True
