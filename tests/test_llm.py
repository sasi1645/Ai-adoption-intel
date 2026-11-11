from ai_adoption_intel.llm import is_safe_sql


def test_allows_select():
    sql = "SELECT * FROM national;"
    result = is_safe_sql(sql)
    assert result == True


def test_allows_lowercase_select():
    sql = "select * from sector"
    result = is_safe_sql(sql)
    assert result == True


def test_blocks_multiple_statements():
    sql = "SELECT COUNT(question_id) FROM national; DROP national;"
    result = is_safe_sql(sql)
    assert result == False


def test_blocks_delete():
    sql = "DELETE FROM sector"
    result = is_safe_sql(sql)
    assert result == False


def test_blocks_mixed_drop_sector():
    sql = "Drop table sector"
    result = is_safe_sql(sql)
    assert result == False


def test_blocks_non_select_start():
    sql = "EXPLAIN SELECT 1"
    result = is_safe_sql(sql)
    assert result == False


def test_blocks_column_containing_forbidden_word():
    sql = "SELECT updated_at FROM orders"
    result = is_safe_sql(sql)
    assert result == False
