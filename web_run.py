from web import app
import os

if __name__ == '__main__':
    for f in os.listdir('temp'):
        try:
            os.remove(os.path.join('temp', f))
        except Exception as e:
            print('Failed to delete temp file. Reason: ', e)
    print('Temp folder clean complete.')

    app.run(host='0.0.0.0', port=8080, debug=True)
