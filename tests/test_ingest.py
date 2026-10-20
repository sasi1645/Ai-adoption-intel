from ai_adoption_intel.ingest import clean_values, drop_footnotes
import pandas as pd
import numpy as np
def test_clean_values():
    data = [["29%"],["S"],["18"],["."],["S"]]
    test_df = pd.DataFrame(data, columns=["value"])
    result_df = clean_values(test_df)
    expected_status = ["ok", "suppressed", "ok", "not_collected", "suppressed"]
    expected_percentage = [29.0,None,18.0,None,None]

    assert result_df["status"].tolist() == expected_status, f"Expected {expected_status}, but got {result_df['status'].tolist()}"
    assert result_df["percentage"].isna().tolist() == [False, True, False, True, True], f"Expected NaN values at indices 1, 3, and 4, but got {result_df['percentage'].isna().to_list()}"
    assert result_df["percentage"].dropna().tolist() == [29.0,18.0], f"Expected non-NaN values to be [29.0, 18.0], but got {result_df['percentage'].dropna().tolist()}"

def test_drop_footnotes():
    data1 = pd.DataFrame({
        'Question ID': ["some", "data", 3, 4, 9],
        'Answer': ["x", "y", "No", "Yes", "Maybe"]})
    result_df_footnote = drop_footnotes(data1, "Question ID")
    expected_df_footnote = [3.0, 4.0, 9.0]
    assert result_df_footnote['Question ID'].tolist()==expected_df_footnote, f"Expected {expected_df_footnote}, but got {result_df_footnote['Question ID'].tolist()}"
