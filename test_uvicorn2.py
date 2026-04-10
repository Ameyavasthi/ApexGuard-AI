import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == '__main__':
    uvicorn.run(
        'test_uvicorn2:app',
        host='0.0.0.0',
        port=8000,
        workers=2,
        loop='asyncio',
        http='h11',
        reload=False,
        access_log=False,
        timeout_keep_alive=5,
        limit_concurrency=20,
        backlog=100,
    )
