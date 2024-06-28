# Passage Generator
import json
import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Question Maker
import torch
from transformers import BertTokenizer, BertForMaskedLM
from nltk.corpus import wordnet as wn

# import nltk
# nltk.download('wordnet')

# Essage Grader
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from huggingface_hub import login



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
        self.max_word_count = int(
            self.max_tokens / self.avg_token_per_word) - 2
        self.max_possible_word_count = int(
            self.max_tokens / self.avg_token_per_word)

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

        combined_text = " ".join(
            [list(paragraph.values())[0] for paragraph in chosen_paragraphs]
        )

        return topic_index, chosen_paragraph_indices, combined_text

    def generate_text(self, word_count=None):
        if word_count is None:
            word_count = self.max_word_count

        if word_count > self.max_possible_word_count:
            print(
                f"Word count exceeds the maximum possible word count of {self.max_possible_word_count} words.")
            word_count = self.max_possible_word_count

        topic_index, chosen_paragraph_indices, combined_text = self.choose_random_topic_and_paragraphs()

        # print(f"Chosen topic number: {topic_index + 1}")
        # print("Chosen paragraphs:")
        # for i, index in enumerate(chosen_paragraph_indices, start=1):
        #     print(f"Paragraph number {i}: {index + 1}")

        inputs = self.tokenizer.encode(
            combined_text, return_tensors='pt', truncation=True)
        # Ensure input length doesn't exceed max_tokens
        max_input_length = min(len(inputs[0]), self.max_tokens)
        inputs = inputs[:, :max_input_length]
        generated_text = combined_text
        generated_token_ids = inputs

        try:
            while self.count_words(generated_text) < word_count:
                remaining_word_count = word_count - \
                    self.count_words(generated_text)
                max_new_tokens = min(int(remaining_word_count * 1.5), self.max_tokens - len(
                    generated_token_ids[0]))  # Adjust max_new_tokens to stay within max_tokens
                outputs = self.model.generate(
                    generated_token_ids,
                    max_length=len(generated_token_ids[0]) + max_new_tokens,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                new_generated_text = self.tokenizer.decode(
                    outputs[0], skip_special_tokens=True)
                if new_generated_text.strip() == "":
                    break  # Stop if no new text is generated to prevent infinite loop
                generated_text = new_generated_text
                generated_token_ids = self.tokenizer.encode(
                    generated_text, return_tensors='pt', truncation=True)
                # Ensure input length doesn't exceed max_tokens
                max_input_length = min(
                    len(generated_token_ids[0]), self.max_tokens)
                generated_token_ids = generated_token_ids[:, :max_input_length]
        except IndexError as e:
            print(
                "An error occurred during text generation. Please try again with a lower word count.")
            return None

        self.generated_text = self.truncate_at_last_full_stop(
            generated_text, word_count)


class QuestionGenerator:
    def __init__(self, model_name='bert-base-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForMaskedLM.from_pretrained(model_name)

    def generate_fill_in_the_blanks(self, sentences, num_questions):
        fill_in_the_blanks_dict = {}
        used_sentences = set()
        
        while len(fill_in_the_blanks_dict) < num_questions:
            if len(used_sentences) == len(sentences):
                break  # If all sentences are used, stop the loop
            
            # Select a batch of sentences that have not been used
            batch_sentences = [sentence for sentence in sentences if sentence not in used_sentences]
            batch_sentences = random.sample(batch_sentences, min(len(batch_sentences), num_questions - len(fill_in_the_blanks_dict)))
            
            # Process each sentence in the batch
            for selected_sentence in batch_sentences:
                used_sentences.add(selected_sentence)
                tokens = self.tokenizer.tokenize(selected_sentence)
                alpha_indices = [i for i, token in enumerate(tokens) if token.isalpha()]
                if not alpha_indices:
                    continue  # Skip if no alphabetic token is found
                
                masked_idx = random.choice(alpha_indices)
                masked_word = tokens[masked_idx]
                tokens[masked_idx] = '[MASK]'
                input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
                input_ids = torch.tensor([input_ids])
                
                # Batch prediction
                with torch.no_grad():
                    outputs = self.model(input_ids)
                    predictions = outputs.logits
                
                masked_idx_tensor = torch.tensor([masked_idx])
                predicted_token_ids = torch.topk(predictions[0, masked_idx_tensor], 5).indices[0].tolist()
                predicted_tokens = self.tokenizer.convert_ids_to_tokens(predicted_token_ids)
                sentence_with_blank = self.tokenizer.convert_tokens_to_string(tokens).replace('[MASK]', '***')
                fill_in_the_blanks_dict[masked_word] = sentence_with_blank
                
                if len(fill_in_the_blanks_dict) >= num_questions:
                    break
        
        return fill_in_the_blanks_dict

    def get_random_word(self, num_words):
        random_words_matrix = []
        synsets = list(wn.all_synsets())

        for _ in range(num_words):
            random_words = []
            for _ in range(3):
                # Get a random synset
                random_synset = random.choice(synsets)
                # Get a random lemma from the synset
                random_word = random.choice(random_synset.lemma_names())
                if random_word not in random_words:
                    random_words.append(random_word)
            random_words_matrix.append(random_words)
        return random_words_matrix
    
    def generate_mcqs(self, sentences, num_questions):
        mcq_questions_list = []
        random_options = self.get_random_word(num_questions)
        used_sentences = set()
        i = 0
        while len(mcq_questions_list) < num_questions:
            selected_sentence = random.choice(sentences)
            if selected_sentence in used_sentences:
                continue
            used_sentences.add(selected_sentence)
            if not selected_sentence.endswith('.'):
                selected_sentence += '.'

            tokens = self.tokenizer.tokenize(selected_sentence)
            masked_idx = random.choice([i for i, token in enumerate(tokens) if token.isalpha()])
            masked_word = tokens[masked_idx]
            tokens[masked_idx] = '[MASK]'
            input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
            input_ids = torch.tensor([input_ids])
            
            with torch.no_grad():
                outputs = self.model(input_ids)
                predictions = outputs.logits
            masked_idx_tensor = torch.tensor([masked_idx])
            predicted_token_ids = torch.topk(predictions[0, masked_idx_tensor], 5).indices[0].tolist()
            predicted_tokens = self.tokenizer.convert_ids_to_tokens(predicted_token_ids)
            options = [masked_word]
            options.extend(random_options[i])
            i+=1
            random.shuffle(options)
            correct_index = options.index(masked_word)
            sentence_with_blank = self.tokenizer.convert_tokens_to_string(tokens).replace('[MASK]', '***')
            mcq_questions_list.append([correct_index, sentence_with_blank, options])
            print("MCQs count:", i)
        return mcq_questions_list
    

class EssayGrader:
    def __init__(self, json_path, hf_token='HUGGINGFACE_TOKEN', model_name='Kevintu/Engessay_grading_ML', tokenizer_name='KevSun/Engessay_grading_ML'):
        self.json_path = json_path
        self.hf_token = hf_token
        self.model_name = model_name
        self.tokenizer_name = tokenizer_name
        self.data = self.load_json()
        self.topics = self.data.get("Topics", [])
        self.model, self.tokenizer = self.load_model_and_tokenizer()

    def handle(self, err_code, err=""):
        codes = {
            11: "The specified JSON file was not found.",
            12: "The JSON file could not be decoded. Please check its format.",
            13: "No topics found in the JSON file",
            14: "No essay was entered. Please provide your essay.",
            15: f"Error logging in to Hugging Face: {err}",
            16: f"Error loading model or tokenizer: {err}",
        }
        print(codes[err_code])
        exit(0)

    def load_json(self):
        try:
            with open(self.json_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.handle(11)
        except json.JSONDecodeError:
            self.handle(12)

    def load_model_and_tokenizer(self):
        try:
            login(self.hf_token, add_to_git_credential=False)
        except Exception as e:
            self.handle(15, e)

        try:
            model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
            return model, tokenizer
        except Exception as e:
            self.handle(16, e)

    def select_topic(self):
        if not self.topics:
            self.handle(13)
        selected_topic = random.choice(self.topics)
        selected_topic_title = selected_topic.get("Topic", "No Title")
        selected_paragraphs = selected_topic.get("Paragraphs", [])
        return selected_topic_title, selected_paragraphs

    def grade_essay(self, essay):
        if not essay:
            self.handle(14)
        encoded_input = self.tokenizer(essay, return_tensors='pt', padding=True, truncation=True, max_length=64)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**encoded_input)
        predictions = outputs.logits.squeeze()
        predicted_scores = predictions.numpy()
        item_names = ["cohesion", "syntax", "vocabulary", "phraseology", "grammar", "conventions"]
        scaled_scores = 2.25 * predicted_scores - 1.25
        rounded_scores = [round(score * 2) / 2 for score in scaled_scores]
        overall_score = round(sum(rounded_scores) / len(rounded_scores) * 2) / 2
        return dict(zip(item_names, rounded_scores)), overall_score
