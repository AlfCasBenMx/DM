from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import random

app = Flask(__name__, template_folder='./templates')
app.secret_key = 'super_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"  # Ensure that session cookie is sent with AJAX requests

# Load the Excel file into a pandas DataFrame
questions_df = pd.read_excel("Study_Questions_v0.1 200.xlsx")

@app.route('/')
def index():
    if 'score' not in session:
        session['score'] = {'correct': 0, 'incorrect': 0}
    
    # Select a random question from the DataFrame
    random_question = questions_df.sample(1).iloc[0]
    session['current_question_id'] = int(random_question['No.'])
    
    options = [
        random_question['OPCIÓN1'],
        random_question['OPCIÓN2'],
        random_question['OPCIÓN3'],
        random_question['OPCIÓN4'],
        random_question['OPCIÓN5']
    ]
    
    return render_template('quiz.html', question=random_question['PREGUNTA'], options=options, score=session['score'], AreaId=int(random_question['AreaId']), Area=random_question['Area'])

@app.route('/new_question')
def new_question():
    random_question = questions_df.sample(1).iloc[0]
    session['current_question_id'] = int(random_question['No.'])
    options = [
        random_question['OPCIÓN1'],
        random_question['OPCIÓN2'],
        random_question['OPCIÓN3'],
        random_question['OPCIÓN4'],
        random_question['OPCIÓN5']
    ]
    return jsonify({
        'question': random_question['PREGUNTA'],
        'options': options,
        'AreaId': int(random_question['AreaId']),  # Ensure it's a native Python int
        'Area': random_question['Area']
    })
@app.route('/reset_score')
def reset_score():
    session['score'] = {'correct': 0, 'incorrect': 0}
    return jsonify(session['score'])


@app.route('/check_answer', methods=['POST'])
def check_answer():
    selected_option = int(request.form['option'])
    question_id = session['current_question_id']
    correct_answer = int(questions_df[questions_df['No.'] == question_id].iloc[0]['RESP'])

    if selected_option == correct_answer:
        session['score']['correct'] += 1
        result = 'Correct!'
    else:
        session['score']['incorrect'] += 1
        result = 'Incorrect!'
    
    session.modified = True

    correct_answer_text = questions_df[questions_df['No.'] == question_id].iloc[0]['OPCIÓN' + str(correct_answer)]
    return jsonify({'result': result, 'score': session['score'], 'correct_answer': correct_answer_text})

if __name__ == '__main__':
    app.run()
