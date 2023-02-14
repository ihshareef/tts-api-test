def separate_text(text):
    paragraphs = []
    words = text.split()
    temp_paragraph = []
    char_count = 0
    for word in words:
        char_count += len(word)
        if char_count > 250 or word == "\n":
            paragraphs.append(" ".join(temp_paragraph))
            temp_paragraph = []
            char_count = 0
        else:
            temp_paragraph.append(word)

    if temp_paragraph:
        paragraphs.append(" ".join(temp_paragraph))

    return paragraphs