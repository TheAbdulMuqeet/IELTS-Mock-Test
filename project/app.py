from flask import Flask, send_file, render_template, abort, jsonify, redirect, request
import os, pyaudio, wave, threading
from TextAndSpeech import text_to_speech, speech_to_text
from dotenv import load_dotenv
from main import TextGenerator, QuestionGenerator, EssayGrader

app = Flask(__name__)
filename = "output.wav"
upload_folder = './static'


@app.route('/speaking/')
def speaking():
    return render_template("speaking.html", topic="Test")

# @app.route('/record/', methods=['POST'])
# def record():
#     path = "./static/upload.wav"
#     if 'audio' not in request.files:
#         return jsonify(status='error', message='No file part'), 400
#     file = request.files['audio']
#     if file.filename == '':
#         return jsonify(status='error', message='No selected file'), 400
#     if file:
#         file.save(path)
#         user_para = speech_to_text(path)
#         return jsonify(status='ok', output=user_para, message="Audio converted successfully.")

@app.route('/listening/')
def get_file():
    return render_template("listening.html") 

@app.route('/writing/')
def writing():
    return render_template('writing.html', topic=topic)

@app.route('/submit-passage', methods=['POST'])
def submit_passage():
    user_para = request.form.get('write-area')
    if user_para:
        bands = ""
        scores, overall_score = para_writing.grade_essay(user_para)
        for item, score in scores.items():
            bands += f"{item} ({score})<br>"
        output = f"Your overall score is {overall_score}. Evaluation metrics are:<br>{bands}"
        return jsonify(status='ok', message=output)
    else:
        return jsonify(status='error', message='No passage provided.')

@app.route('/reading/')
def reading():
    return render_template("reading.html", passage=passage)


@app.route('/get-mcqs/')
def get_mcqs():
    return jsonify(mcqs)


@app.route('/get-blanks', methods=['GET'])
def get_blanks():
    return jsonify(blanks)


# @app.route('/get-questions/')
# def get_qna():
#     questions = [
#         ["What is a cat?", "Cat is an animal"],
#         ["How do you know it works?", "Because it works."]
#     ]
#     return jsonify(questions)


# @app.route('/submit-questions', methods=['POST'])
# def submit_questions():
#     data = request.get_json()
#     print(data)
#     questions = data.get('questions', [])
#     return jsonify(status='ok')

@app.route('/', methods=['GET'])
def home():
    return redirect("/reading")

if __name__ == '__main__':
    load_dotenv()
    test = QuestionGenerator()
    global passage, blanks, mcqs, topic, para_writing

    print("Initializing the process...")
    generator = TextGenerator(json_path=os.getenv("JSON_PATH"))
    generator.generate_text(word_count=int(os.getenv("WORD_COUNT")))
    print("Generating passage...")

    passage = generator.generated_text
    print("Generating audio...")
    text_to_speech(passage)

    sentences = [sentence.strip() for sentence in passage.split('. ') if sentence]
    print("Tokenizing Sentences...")

    print("Generating MCQs...")
    mcqs = test.generate_mcqs(sentences, num_questions=int(os.getenv("MCQ_COUNT")))
    print("Generated MCQs Count:", len(mcqs))

    print("Generating Blanks...")
    blanks = test.generate_fill_in_the_blanks(sentences, num_questions=int(os.getenv("BLANKS_COUNT")))
    print("Generated Blanks Count:", len(blanks))

    para_writing = EssayGrader(json_path=os.getenv("JSON_PATH"))
    topic, _ = para_writing.select_topic()

    app.run()
