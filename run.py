from inboxbird import app
import os

debug = False if os.environ.get('DEBUG') else True
if debug:
    app.config['SERVER_NAME'] = 'localhost:5000'

if __name__ == '__main__':
    print "Flask app running at http://0.0.0.0:5000"
    app.run(debug=debug, port=5000, threaded=True)
