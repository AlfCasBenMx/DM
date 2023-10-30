from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import random

app = Flask(__name__, template_folder='./templates')
app.secret_key = 'super_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"  # Ensure that session cookie is sent with AJAX requests

# Load the Excel file into a pandas DataFrame
questions_df = pd.read_excel("Study_Questions_v0.1 200_modified.xlsx")

@app.route('/')
def index():
    if 'score' not in session:
        session['score'] = {'correct': 0, 'incorrect': 0, 'by_area': {}}

    
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
    print()
    return render_template('quiz.html', question=random_question['PREGUNTA'], options=options, score=session['score'], AreaId=int(random_question['AreaId']), Area=random_question['Area'],correct_answer=int(random_question['RESP']))
@app.route('/new_question')
def new_question():
    # Reload the Excel file into the DataFrame
    global questions_df
    questions_df = pd.read_excel("Study_Questions_v0.1 200_modified.xlsx")
    
    random_question = questions_df.sample(1).iloc[0]
    session['current_question_id'] = int(random_question['No.'])
    options = [
        random_question['OPCIÓN1'],
        random_question['OPCIÓN2'],
        random_question['OPCIÓN3'],
        random_question['OPCIÓN4'],
        random_question['OPCIÓN5']
    ]
    
    correct_count = random_question['Correcto'] if not pd.isna(random_question['Correcto']) else 0
    incorrect_count = random_question['Incorrecto'] if not pd.isna(random_question['Incorrecto']) else 0

    response_data = {
        'question': random_question['PREGUNTA'],
        'options': options,
        'AreaId': int(random_question['AreaId']),
        'Area': random_question['Area'],
        'correct_answer': int(random_question['RESP']),
        'correct_count': int(correct_count),
        'incorrect_count': int(incorrect_count)
    }
    print(response_data)
    return jsonify(response_data)
@app.route('/reset_score')
def reset_score():
    session['score'] = {'correct': 0, 'incorrect': 0}
    return jsonify(session['score'])

@app.route('/check_answer', methods=['POST'])
def check_answer():
    selected_option = int(request.form['option'])
    question_id = session['current_question_id']
    current_question = questions_df[questions_df['No.'] == question_id].iloc[0]
    correct_answer = int(current_question['RESP'])

    if 'by_area' not in session['score']:
        session['score']['by_area'] = {}

    area = current_question['Area']
    if area not in session['score']['by_area']:
        session['score']['by_area'][area] = {'correct': 0, 'incorrect': 0}

    correct_count = 0 if pd.isna(current_question['Correcto']) else int(current_question['Correcto'])
    incorrect_count = 0 if pd.isna(current_question['Incorrecto']) else int(current_question['Incorrecto'])

    if selected_option == correct_answer:
        session['score']['correct'] += 1
        session['score']['by_area'][area]['correct'] += 1
        correct_count += 1
        questions_df.loc[questions_df['No.'] == question_id, 'Correcto'] = correct_count
        result = 'Correct!'
    else:
        session['score']['incorrect'] += 1
        session['score']['by_area'][area]['incorrect'] += 1
        incorrect_count += 1
        questions_df.loc[questions_df['No.'] == question_id, 'Incorrecto'] = incorrect_count
        result = 'Incorrect!'

    session.modified = True

    # Guardar los cambios en el archivo Excel
    try:
        questions_df.to_excel("Study_Questions_v0.1 200_modified.xlsx", index=False)
        save_status = "Data saved successfully to Excel"
    except Exception as e:
        save_status = f"Error saving to Excel: {str(e)}"

    return jsonify({'result': result, 'score': session['score'], 'correct_answer': correct_answer, 'save_status': save_status})




@app.route('/add_comment', methods=['POST'])
def add_comment():
    question_id = session['current_question_id']
    comment = request.form['comment']
    
    # Load the Excel file
    df = pd.read_excel("Study_Questions_v0.1 200_modified.xlsx")
    
    # Add the comment to the appropriate row
    df.loc[df['No.'] == question_id, 'Comments'] = comment
    
    # Save the modified DataFrame back to the Excel file
    df.to_excel("Study_Questions_v0.1 200_modified.xlsx", index=False)
    
    return jsonify({'status': 'Comment added successfully'})

@app.route('/scores_by_area')
def scores_by_area():
    if 'score' not in session or 'by_area' not in session['score']:
        return jsonify({})  # Return empty data if there's no score data in the session

    return jsonify(session['score']['by_area'])


if __name__ == '__main__':
    app.run()

