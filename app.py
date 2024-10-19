from app import app
from livereload import Server

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.serve()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080, debug=True)