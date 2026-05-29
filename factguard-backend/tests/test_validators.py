from app.utils.validators import contains_sql_injection_pattern


def test_clean_text():
    assert not contains_sql_injection_pattern("The Earth is round")


def test_sql_union():
    assert contains_sql_injection_pattern("SELECT * FROM users")
    assert contains_sql_injection_pattern("union select")


def test_sql_drop():
    assert contains_sql_injection_pattern("drop table claims")


def test_sql_exec():
    assert contains_sql_injection_pattern("exec('malicious')")


def test_edge_cases():
    assert not contains_sql_injection_pattern("")
    assert not contains_sql_injection_pattern("a" * 1000)
