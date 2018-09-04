def get_text_paragraph(paragraph_array, format_function):
    """
    will return text from the first paragraph with text

    @param paragraph_array - should be xml elements
    @param format_function - formats the text_content before checking length
    """
    return_value = "No text found"
    for paragraph in paragraph_array:
        # formats and removes leading white space
        text = format_function(paragraph.text_content()).lstrip()
        if (len(text) > 0):
            return_value = text
            break
    return return_value
