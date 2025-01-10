from flask import Flask, request, jsonify
import os
import check
import mysql.connector
from mysql.connector import Error, IntegrityError
from flask_cors import CORS  # Import flask_cors for CORS support

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'LETScode5599$',
    'database': 'moji_main'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/home', methods=['GET'])
def home():
    return "Server is running"

@app.route('/getomr', methods=['POST'])
def get_omr():
    try:
        # Check if the image file is in the request
        if 'image' not in request.files:
            return jsonify({
                'message': 'No image file found in the request',
                'serial_number':'0'
                }), 400

        image_file = request.files['image']

        # Ensure the uploaded file has a filename
        if image_file.filename == '':
            return jsonify({'message': 'No selected file','serial_number':'0'}), 400

        # Check if the request is JSON or Form-data
        if request.is_json:
            data = request.get_json()  # Use .get_json() for JSON data
        else:
            data = request.form  # Use .form for form-data

        # Get examId from the data (handling both JSON and form data)
        exam_id = data.get('examId') if data else None
        if not exam_id:
            return jsonify({'message': 'Exam ID is required','serial_number':'0'}), 400

        # Save the file temporarily
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(image_path)
        print("gettin omr data")
        # Process the OMR image
        omrData = check.check(image_path)
        #----testing data----#
        print(omrData)
        #----data is good---#
        #getting serial number
        serialNumber = next(iter(omrData))
        if serialNumber<1000:
            return jsonify({'message': 'Invalid Serial Number','serial_number':serialNumber}), 404
        # Establish DB connection
        db_connection = get_db_connection()
        cursor = db_connection.cursor()

        # Check if the serialNumber and examId combination exists in the candidate table
        cursor.execute("SELECT * FROM candidates WHERE exam_id = %s AND serial_number = %s", (exam_id, serialNumber))
        candidate_data = cursor.fetchone()

        if not candidate_data:
            return jsonify({'message': 'Candidate not found','serial_number':serialNumber}), 404


        # Query the exam table for the question count based on examId
        cursor.execute("SELECT question_count FROM exams WHERE exam_id = %s", (exam_id,))
        exam_data = cursor.fetchone()
        if not exam_data:
            return jsonify({'message': 'Exam not found','serial_number':serialNumber}), 404

        question_count = exam_data[0]
        print("question count ", question_count)
        
        # Query question_answers for correct answers for the examId and question_set_id = 1
        cursor.execute("""
            SELECT question_number, correct_answer 
            FROM question_answers 
            WHERE exam_id = %s AND question_set_id = 1
        """, (exam_id,))
        correct_answers_data = cursor.fetchall()

        # Create a dictionary for correct answers by question number
        correct_answers_dict = {row[0]: row[1] for row in correct_answers_data}

        correct_answers = 0
        incorrect_answers = 0

        # Iterate over the answers obtained from the OMR and compare with correct answers
        for i in range(question_count):
            omrAnswer = omrData[serialNumber][i][i + 1]  # Get the answer from the OMR image or default to -1 for missing answers
            correct_answer = correct_answers_dict.get(i + 1)  # Get the correct answer based on question number (1-based index)
            print(f"omr answer {omrData} : correct answer: {correct_answer}")
            if omrAnswer == correct_answer:
                correct_answers += 1
            elif omrAnswer == -1 or omrAnswer != correct_answer:
                incorrect_answers += 1

        # Calculate grade based on correct and incorrect answers
        total_answers = correct_answers + incorrect_answers
        grade = "Fail"
        if total_answers > 0:
            grade = "Pass" if (correct_answers / total_answers) > 0.4 else "Fail"

        # Insert the result into the results table
        try:
            cursor.execute("""
                INSERT INTO results (exam_id, serial_number, correct_answers, incorrect_answers, grade) 
                VALUES (%s, %s, %s, %s, %s)
            """, (exam_id, serialNumber, correct_answers, incorrect_answers, grade))  # Assuming serial_number is 1005

            db_connection.commit()
        
        except IntegrityError as e:
            if e.errno == 1062:  # Duplicate entry error code
                return jsonify({'message': 'Result Already Exist','serial_number':serialNumber}), 409
        
        cursor.close()
        db_connection.close()

        # Remove the uploaded image after processing
        os.remove(image_path)
        
        return jsonify({
            'serial_number':serialNumber,
            'total_question':question_count,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'grade': grade,
            'message': 'Image received and processed successfully',
        }), 200

    except Exception as e:
        return jsonify({'message': 'Unknown paper format or server error','serial_number':0}), 500
    finally:
        # Remove the uploaded image after processing
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            
if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=5000)


