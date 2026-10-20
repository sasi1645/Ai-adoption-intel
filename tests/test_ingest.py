from ai_adoption_intel.ingest import clean_values
import pandas as pd
def test_clean_values():
    data = [["29%"],["S"],["18"],["."],["S"]]
    test_df = pd.DataFrame(data, columns=["value"])
    result_df = clean_values(test_df)
    expected_status = ["ok", "suppressed", "ok", "not_collected", "suppressed"]
    expected_percentage = [29.0,None,18.0,None,None]

    assert result_df["status"].tolist() == expected_status, f"Expected {expected_status}, but got {result_df['status'].tolist()}"
    #assert result_df["percentage"].tolist() == expected_percentage, f"Expected {expected_percentage}, but got {result_df['percentage'].tolist()}"
    assert result_df["percentage"].isna().tolist() == [False, True, False, True, True], f"Expected NaN values at indices 1, 3, and 4, but got {result_df['percentage'].isna().to_list()}"
    assert result_df["percentage"].dropna().tolist() == [29.0,18.0], f"Expected non-NaN values to be [29.0, 18.0], but got {result_df['percentage'].dropna().tolist()}"