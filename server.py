import asyncio, aiohttp
import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=[
                   '*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='static'))
# app.wsgi_app = ProxyFix(app.wsgi_app)

# export_file_url = r'https://is.gd/acfAOG'
export_file_url = r"https://is.gd/flgMdy"
export_file_name = 'pokemon_resnet18_73acc.pkl'

path = Path(__file__).parent

# Read class names from file
file_path = Path("pokemons.txt")

with open(file_path) as file:
    classes = file.readlines()


async def download_file(url, dest):
    if dest.exists():
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            model_pkl = await response.read()
            with open(dest, 'wb') as f:
                f.write(model_pkl)


async def setup_learner():
    """Downloads the learner from link and saves it for the session"""
    await download_file(export_file_url, path / export_file_name)
    try:
        model = load_learner(path, export_file_name)
        return model
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\
                        \n\nPlease update the fastai library in your training environment and export your model again.\
                        \n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


# loop = asyncio.get_event_loop()
# # Setup learner task
# tasks = [asyncio.ensure_future(setup_learner())]
# # get model object
# learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
# loop.close()

loop = asyncio.get_event_loop()
# Setup learner task
tasks = [asyncio.ensure_future(setup_learner())]
# get model object
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

# @app.route('/hello')
# def hello_world():
#     return 'Hello, World!'


@app.route('/')
def home(request):
    # return render_template("index.html")
    html_file = path / 'templates' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/predict', methods=['POST'])
async def predict(request):
    # get data from web form
    img_data = await request.form()
    # read image data from form
    img_bytes = await (img_data['file'].read())
    # convert bytes to Image object
    img = open_image(BytesIO(img_bytes))
    # Make prediction
    prediction = learn.predict(img)[0]
    return JSONResponse({'result': str(prediction)})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
