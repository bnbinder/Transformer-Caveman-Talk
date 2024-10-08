import torch
import transformers
from huggingface_hub import login
import spacy
import re
from spacy.tokens import Doc, Span

login("hhhh")
nlp = spacy.load("en_core_web_sm")

class Llama3:
    def __init__ (self, modelPath):
        self.modelID = modelPath
        self.pipeline = transformers.pipeline(
            "text-generation",
            model = self.modelID,
            model_kwargs = {
                "torch_dtype": torch.float16,
                "quantization_config": {"load_in_4bit": True},
                "low_cpu_mem_usage": True,
            },
        )
        
        self.terminator = self.pipeline.tokenizer.eos_token_id
        
    def getResponse (self, query, maxTokens = 4096, temp = 0.6, topP = 0.9):
        userPrompt = [{"role": "system", "content": ""}] + [{"role": "user", "content": query}]
        prompt = self.pipeline.tokenizer.apply_chat_template(
            userPrompt, tokenize=False, add_generation_prompt=True
        )
        outputs = self.pipeline(
            prompt,
            max_new_tokens = maxTokens,
            eos_token_id = self.terminator,
            do_sample = True,
            temperature = temp,
            top_p = topP
        )
        response = outputs[0]["generated_text"][len(prompt):]
        return response
    
    def generateSentences (self):
        while True:
            userInput = input("Ask the AI to write something or write \"theme\" and a theme after for it to generate some sentences based on the theme: ")
            response = ""
            if(userInput.lower().replace("\"", "")[:5] == "theme"):
                response = self.getResponse("Using this theme, generate at least five sentences in paragraph form. Do not include any introduction sentence responding to my prompt, only respond with the sentences generated. So something like \"Here are five sentences in paragraph form:\" do not include: " + userInput)
            else:
                response = self.getResponse("Do not include any introduction sentence responding to my prompt, only respond with the sentences generated. So something like \"Here are five sentences in paragraph form:\" do not include: " + userInput)
            print("What Llama cooked up: " + response)
            yorn = input("Is this good (Yes/No)").lower()[0]
            if(yorn == "y"):
                return response
    
    def lemmasDoc(self, text, nlp):
        doc = nlp(text)
        lemmas = [token.lemma_ for token in doc]
        simpWord = ' '.join(lemmas)
        simpWord = re.sub(r'\s+', ' ', simpWord)
        simpWord = re.sub(r' \.', '.', simpWord)
        simpWord = re.sub(r' \?', '?', simpWord)
        simpWord = re.sub(r' \,', ',', simpWord)
        simpWord = re.sub(r' \'', '', simpWord)
        simpWord = simpWord.strip()
        doc = nlp(simpWord)
        return doc
    
    def caveManModify (self):
        while True:
            words = []
            output = self.generateSentences()
            doc = self.lemmasDoc(output, nlp)
            for token in doc:
                if token.tag_ in ["MD", "JJR", "JJS"]:
                    continue
                if token.dep_ in ["det"]:
                    continue
                if token.text in ["my", "to"]:
                    continue
                if token.pos_ == "ADJ" and token.text != token.lemma_[:len(token.text) - 1]:
                    words.append(token.text)
                    continue
                words.append(token.lemma_)
            word = []
            word.append(' '.join(words).capitalize())
            simpWord = ' '.join(word)
            simpWord = re.sub(r'\s+', ' ', simpWord)
            simpWord = re.sub(r' \.', '.', simpWord)
            simpWord = re.sub(r' \?', '?', simpWord)
            simpWord = re.sub(r' \'', '', simpWord)
            simpWord = re.sub(r' \,', ',', simpWord)
            simpWord = simpWord.strip()
            print(simpWord)
            break


def test(text):
    doc = lemmasDoctest(text, nlp)   
    for token in doc:
        print(f"Text: {token.text}\n"
                f"Lemma: {token.lemma_}\n"
                f"POS: {token.pos_}\n"
                f"Tag: {token.tag_}\n"
                f"Dep: {token.dep_}\n"
                f"Shape: {token.shape_}\n"
                f"Is Alpha: {token.is_alpha}\n"
                f"Is Stop: {token.is_stop}\n"
                f"Is Punct: {token.is_punct}\n"
                f"Like Num: {token.like_num}\n"
                f"Ent IOB: {token.ent_iob_}\n"
                f"Ent Type: {token.ent_type_}\n")

def lemmasDoctest(text, nlp):
        doc = nlp(text)
        lemmas = [token.lemma_ for token in doc]
        simpWord = ' '.join(lemmas)
        simpWord = re.sub(r'\s+', ' ', simpWord)
        simpWord = re.sub(r' \.', '.', simpWord)
        simpWord = re.sub(r' \?', '?', simpWord)
        simpWord = re.sub(r' \,', ',', simpWord)
        simpWord = re.sub(r'\'', '', simpWord)
        simpWord = simpWord.strip()
        doc = nlp(simpWord)
        return doc
    
def caveManModifytest ():
    while True:
        words = []
        output ="""The sky was a deep shade of indigo, with clouds that seemed to be painted by a master artist. The stars twinkled like 
diamonds scattered across the velvet expanse, and the moon glowed with a soft, gentle light. As the sun began to set, the colors of the sky 
deepened, a fiery orange and crimson bleeding into the darkness. The air was filled with the sweet scent of blooming flowers, and the sound 
of crickets provided a soothing background hum. As the night wore on, the stars seemed to grow brighter, and the world felt full of magic and wonder."""            
        print(output)
        doc = lemmasDoctest(output, nlp)
        for token in doc:
            if token.tag_ in ["MD", "JJR", "JJS"]:
                continue
            if token.dep_ in ["det"]:
                continue
            if token.text in ["my", "to", "its"]:
                continue
            if token.pos_ == "ADJ" and token.text != token.lemma_[:len(token.text) - 1]:
                words.append(token.text)
                continue
            words.append(token.lemma_)
        word = []
        word.append(' '.join(words).capitalize())
        simpWord = ' '.join(word)
        simpWord = re.sub(r'\s+', ' ', simpWord)
        simpWord = re.sub(r' \.', '.', simpWord)
        simpWord = re.sub(r' \?', '?', simpWord)
        simpWord = re.sub(r' \,', ',', simpWord)
        simpWord = re.sub(r'\'', '', simpWord)
        simpWord = simpWord.strip()
        print(simpWord)
        break

if __name__ == "__main__":
    bot = Llama3("meta-llama/Meta-Llama-3-8B-Instruct")
    bot.caveManModify()
    #caveManModifytest()
#    test("""The sky was a deep shade of indigo, with clouds that seemed to be painted by a master artist. The stars twinkled like 
#diamonds scattered across the velvet expanse, and the moon glowed with a soft, gentle light. As the sun began to set, the colors of the sky 
#deepened, a fiery orange and crimson bleeding into the darkness. The air was filled with the sweet scent of blooming flowers, and the sound 
#of crickets provided a soothing background hum. As the night wore on, the stars seemed to grow brighter, and the world felt full of magic and wonder."""            )
   
   
   
    #test("bright brighter")
#    test( """The sky was a deep shade of indigo, with clouds that seemed to be painted by a master artist. The stars twinkled like 
#diamonds scattered across the velvet expanse, and the moon glowed with a soft, gentle light. As the sun began to set, the colors of the sky 
#deepened, a fiery orange and crimson bleeding into the darkness. The air was filled with the sweet scent of blooming flowers, and the sound 
#of crickets provided a soothing background hum. As the night wore on, the stars seemed to grow brighter, and the world felt full of magic and wonder."""            )
            