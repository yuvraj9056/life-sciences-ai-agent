import re


class TextCleaner:

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return ""

        # Replace multiple whitespaces/newlines with a single space
        text = re.sub(r"\s+", " ", text)

        # Remove null characters
        text = text.replace("\x00", "")

        # Strip leading/trailing whitespace
        text = text.strip()

        return text