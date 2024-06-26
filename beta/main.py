import json
import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class TextGenerator:
    def __init__(self, json_path, model_name='gpt2', word_count=180):
        self.json_path = json_path
        self.model_name = model_name
        self.word_count = word_count
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.data = self.load_json()
        self.max_tokens = 1024
        self.avg_token_per_word = 1.33
        self.max_word_count = int(self.max_tokens / self.avg_token_per_word) - 2
        self.max_possible_word_count = int(self.max_tokens / self.avg_token_per_word)

    def load_json(self):
        with open(self.json_path, 'r') as file:
            return json.load(file)

    def count_words(self, text):
        return len(text.split())

    def truncate_at_last_full_stop(self, text, word_count):
        words = text.split()
        truncated_text = " ".join(words[:word_count])
        last_full_stop_index = truncated_text.rfind('.')
        if last_full_stop_index != -1:
            truncated_text = truncated_text[:last_full_stop_index + 1]
        return truncated_text

    def choose_random_topic_and_paragraphs(self):
        topics = self.data.get('Topics', [])
        if not topics:
            raise ValueError("No topics found in the JSON file.")

        topic_index = random.randint(0, len(topics) - 1)
        chosen_topic = topics[topic_index]

        paragraphs = chosen_topic.get('Paragraphs', [])
        if len(paragraphs) < 3:
            raise ValueError("Not enough paragraphs to choose from.")

        chosen_paragraph_indices = random.sample(range(len(paragraphs)), 3)
        chosen_paragraphs = [paragraphs[i] for i in chosen_paragraph_indices]

        combined_text = " ".join([list(paragraph.values())[0] for paragraph in chosen_paragraphs])

        return topic_index, chosen_paragraph_indices, combined_text

    def generate_text(self, word_count=None):
      if word_count is None:
          word_count = self.max_word_count

      if word_count > self.max_possible_word_count:
          print(f"Word count exceeds the maximum possible word count of {self.max_possible_word_count} words.")
          word_count = self.max_possible_word_count

      topic_index, chosen_paragraph_indices, combined_text = self.choose_random_topic_and_paragraphs()

      print(f"Chosen topic number: {topic_index + 1}")
      print("Chosen paragraphs:")
      for i, index in enumerate(chosen_paragraph_indices, start=1):
          print(f"Paragraph number {i}: {index + 1}")

      inputs = self.tokenizer.encode(combined_text, return_tensors='pt', truncation=True)
      max_input_length = min(len(inputs[0]), self.max_tokens)  # Ensure input length doesn't exceed max_tokens
      inputs = inputs[:, :max_input_length]
      generated_text = combined_text
      generated_token_ids = inputs

      try:
          while self.count_words(generated_text) < word_count:
              remaining_word_count = word_count - self.count_words(generated_text)
              max_new_tokens = min(int(remaining_word_count * 1.5), self.max_tokens - len(generated_token_ids[0]))  # Adjust max_new_tokens to stay within max_tokens
              outputs = self.model.generate(
                  generated_token_ids,
                  max_length=len(generated_token_ids[0]) + max_new_tokens,
                  num_return_sequences=1,
                  pad_token_id=self.tokenizer.eos_token_id
              )
              new_generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
              if new_generated_text.strip() == "":
                  break  # Stop if no new text is generated to prevent infinite loop
              generated_text = new_generated_text
              generated_token_ids = self.tokenizer.encode(generated_text, return_tensors='pt', truncation=True)
              max_input_length = min(len(generated_token_ids[0]), self.max_tokens)  # Ensure input length doesn't exceed max_tokens
              generated_token_ids = generated_token_ids[:, :max_input_length]
      except IndexError as e:
          print("An error occurred during text generation. Please try again with a lower word count.")
          return None

      self.generated_text = self.truncate_at_last_full_stop(generated_text, word_count)


generator = TextGenerator(json_path='D:\\NLP\main.json')

# word_count generate the number of words you want to generated by model. they can be 180 , 240 etc. but not more than 769.
generator.generate_text(word_count=1200) # Specify the desired word count
print(f"Generated text:\n{generator.generated_text}")