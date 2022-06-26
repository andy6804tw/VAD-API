from app import app
import config

@app.route('/')
def index():
      return 'server started on '+str(config.PORT)+' PORT '+str(config.ENV)
  

if __name__ == '__main__':
    print(app.url_map)
    app.run(host='0.0.0.0', port=config.PORT, debug=False)
