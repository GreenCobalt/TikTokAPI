from app.main import Host_IP, Host_Port
import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', host=Host_IP, port=Host_Port, reload=False, log_level="info")