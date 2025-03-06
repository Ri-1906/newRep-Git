from flask import Flask, request, jsonify, render_template, send_file, Response
import os
import json
import tempfile
import time
from werkzeug.utils import secure_filename
import meeting_summarizer  
from pydub import AudioSegment
from pydub import AudioSegment

AudioSegment.converter = r"C:\Users\Riddhi\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\Riddhi\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffprobe.exe"

import logging

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

# Create the uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable to store active summarizer instance
active_summarizer = None

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload for audio processing."""
    logging.debug("Received file upload request")
    if 'file' not in request.files:
        logging.error("No file part in the request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logging.debug(f"Saving file to {file_path}")
        file.save(file_path)
        
        # Initialize summarizer and process the file
        try:
            global active_summarizer
            active_summarizer = meeting_summarizer.create_summarizer()
            
            # Convert and transcribe the audio
            logging.debug("Converting audio")
            converted_path = active_summarizer.convert_audio(file_path)
            logging.debug("Transcribing audio")
            transcript = active_summarizer.transcribe_audio(converted_path)
            
            # Process transcript
            logging.debug("Processing transcript")
            results = active_summarizer.process_transcript()
            
            return jsonify({
                'success': True, 
                'filename': filename, 
                'transcript': transcript, 
                'summary': results.get("summary", "No summary available"),
                'key_points': results.get("key_points", []),
                'entities': results.get("entities", {}),
                'action_items': results.get("action_items", []),
                'decisions': results.get("decisions", []),
                'participants': results.get("participants", [])
            })
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/record', methods=['POST'])
def start_recording():
    """Start recording from microphone."""
    try:
        data = request.json
        recording_seconds = int(data.get('seconds', 60))
        
        # Initialize summarizer
        global active_summarizer
        active_summarizer = meeting_summarizer.create_summarizer()
        
        # Record audio
        audio_path = active_summarizer.record_audio(seconds=recording_seconds)
        
        # Transcribe the recorded audio
        transcript = active_summarizer.transcribe_audio(audio_path)
        
        # Process transcript
        results = active_summarizer.process_transcript()
        
        return jsonify({
            'success': True, 
            'transcript': transcript, 
            'summary': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/live-transcription', methods=['GET'])
def live_transcription():
    """Stream live transcription results."""
    def generate():
        global active_summarizer
        if not active_summarizer:
            active_summarizer = meeting_summarizer.create_summarizer()
        
        for transcript_segment in active_summarizer.live_transcription_generator():
            yield f"data: {json.dumps({'segment': transcript_segment})}\n\n"
            time.sleep(0.1)  # Small delay to avoid overwhelming the client
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop-transcription', methods=['POST'])
def stop_transcription():
    """Stop live transcription and process results."""
    global active_summarizer
    if not active_summarizer:
        return jsonify({'error': 'No active transcription session'}), 400
    
    # Process transcript
    results = active_summarizer.process_transcript()
    
    return jsonify({
        'success': True,
        'transcript': active_summarizer.transcript,
        'summary': results
    })

@app.route('/api/process-text', methods=['POST'])
def process_text():
    """Process text transcript directly."""
    try:
        data = request.json
        transcript = data.get('transcript', '')
        
        if not transcript.strip():
            return jsonify({'error': 'Empty transcript'}), 400
        
        # Initialize summarizer
        global active_summarizer
        active_summarizer = meeting_summarizer.create_summarizer()
        
        # Process transcript
        results = active_summarizer.process_transcript(transcript)
        
        return jsonify({
            'success': True,
            'summary': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_summary():
    """Export summary in the requested format."""
    global active_summarizer
    if not active_summarizer:
        return jsonify({'error': 'No active session to export'}), 400
    
    try:
        data = request.json
        format_type = data.get('format', 'markdown')
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format_type}') as tmp:
            temp_filename = tmp.name
        
        # Generate output
        output = active_summarizer.generate_output(format_type, temp_filename)
        
        # If it's CSV format, it creates multiple files
        if format_type == 'csv':
            # Create a zip file of all generated CSVs (this part would need additional code)
            return jsonify({'error': 'CSV export via API not fully implemented'}), 501
        
        # For other formats, return the file
        return send_file(
            temp_filename,
            as_attachment=True,
            download_name=f'meeting_summary.{format_type}',
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-tasks', methods=['POST'])
def export_tasks():
    """Export tasks to external task management system."""
    global active_summarizer
    if not active_summarizer:
        return jsonify({'error': 'No active session to export tasks from'}), 400
    
    try:
        data = request.json
        system_name = data.get('system')
        credentials = data.get('credentials')
        
        if not system_name:
            return jsonify({'error': 'No task system specified'}), 400
        
        # Export tasks
        result = active_summarizer.export_to_task_system(system_name, credentials)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)