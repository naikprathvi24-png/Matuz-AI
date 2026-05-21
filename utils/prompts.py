def summary_prompt(notes):

    return f"""
    Analyze the following notes carefully.

    Provide:

    1. Short Summary
    2. Important Points
    3. 5 Questions and Answers

    Notes:
    {notes}
    """