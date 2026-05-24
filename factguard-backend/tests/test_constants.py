from app.utils.constants import (
    VALID_VERDICTS,
    VALID_CONFIDENCES,
    VALID_STANCES,
    VALID_STATUSES,
)


class TestConstants:
    def test_valid_verdicts(self):
        assert "Verified" in VALID_VERDICTS
        assert "Likely True" in VALID_VERDICTS
        assert "Mixed Evidence" in VALID_VERDICTS
        assert "Likely Misleading" in VALID_VERDICTS
        assert "Unverified" in VALID_VERDICTS
        assert len(VALID_VERDICTS) == 5

    def test_valid_confidences(self):
        assert VALID_CONFIDENCES == {"High", "Medium", "Low"}

    def test_valid_stances(self):
        assert VALID_STANCES == {"supports", "contradicts", "neutral"}

    def test_valid_statuses(self):
        assert VALID_STATUSES == {"pending", "processing", "done", "error"}
