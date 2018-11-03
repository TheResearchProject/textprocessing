class TextProcessor():
    WORD_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
    
    def check_char_type(self, char):
        return "word" if char.lower() in self.WORD_CHARACTERS else "non-word"
        
    def parse_text(self, text):
        """
        Iterates over a text, returning chunks of text, alternating between 
            word and non-word chunks.
        Yields: chunk_type, chunk
                chunk_type = "word" or "non-word"
                chunk      = the chunk of text
        """
        #This keeps track if it's a word or non-word character
        last_char_type = ""
        current_string = ""
        for char in text:
            if last_char_type == "":
                current_string = char
                last_char_type = self.check_char_type(char)
            else:
                current_char_type = self.check_char_type(char)
                if current_char_type != last_char_type:
                    yield last_char_type, current_string
                    last_char_type = current_char_type
                    current_string = char
                else:
                    current_string += char
        yield last_char_type, current_string
        
    def process_text(self, function, text):
        """
        Returns a new version of a text, processing every word with the function
            given. The function should accept a word and return it's processed 
            form.
        """
        resulting_text = ""
        for word_type, word in self.parse_text(text):
            if word_type == "word":
                resulting_text += function(word)
            else:
                resulting_text += word
        return resulting_text
    
if __name__ == "__main__":
    #Some simple test
    from pattern.en import lemma as lemmatizer_en
    tp = TextProcessor()
    tekst = "Generators simplifies creation of iterators. A generator is a function that produces a sequence of results instead of a single value."
    print tp.process_text(lemmatizer_en, tekst)
