from app import app

# Vercel serverless function entry point
def handler(request, response):
    return app(request, response)