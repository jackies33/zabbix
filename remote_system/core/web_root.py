



from fastapi import FastAPI, HTTPException, Request
#from handler_core import Handler_WebHook
from my_env import zbx_web_host

app = FastAPI()

@app.post('/netbox_webhook')
async def webhook(request: Request):
    data = await request.json()
    print(data)
    #handler = Handler_WebHook(data)
    #handler.core_handler()

    return {"message": "success"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=zbx_web_host, port=3501)



