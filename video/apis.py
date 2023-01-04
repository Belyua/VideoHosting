import shutil
from fastapi import UploadFile, Depends, File, APIRouter, Form, BackgroundTasks, HTTPException
from starlette.requests import Request
from starlette.responses import StreamingResponse, HTMLResponse
from user.auth import get_user
from user.models import User
from video.models import Video
from .services import save_video, open_file
from .schemas import UploadVideo, GetVideo, Message
from starlette.templating import Jinja2Templates


video_router = APIRouter(prefix='/video', tags=["video"])
templates = Jinja2Templates(directory="templates")


@video_router.post("/", response_model=GetVideo)
async def create_video(
        back_tasks: BackgroundTasks,
        title: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...),
        user: User = Depends(get_user)
):
    return await save_video(user, file, title, description, back_tasks)


@video_router.get("/video/{video_pk}", response_model=GetVideo, responses={404: {"model": Message}})
async def get_video(video_pk: int):
    return await Video.objects.select_related('user').get(pk=video_pk)


@video_router.get("/index/{video_pk}", response_class=HTMLResponse)
async def get_video(request: Request, video_pk: int):
    return templates.TemplateResponse("index.html", {"request": request, "path": video_pk})


@video_router.get("/video/{video_pk}")
async def get_streaming_video(request: Request, video_pk: int) -> StreamingResponse:
    file, status_code, content_length, headers = await open_file(request, video_pk)
    response = StreamingResponse(
        file,
        media_type='video/mp4',
        status_code=status_code,
    )

    response.headers.update({
        'Accept-Ranges': 'bytes',
        'Content-Length': str(content_length),
        **headers,
    })
    return response


@video_router.get("/404", response_class=HTMLResponse)
async def error_404(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})


@video_router.post("/{video_pk}", status_code=201)
async def add_like(video_pk: int, user: User = Depends(get_user)):
    _video = await Video.objects.select_related("like_user").get(pk=video_pk)
    _user = await User.objects.get(id=user.id)
    if _user in _video.like_user:
        _video.like_count -= 1
        await _video.like_user.remove(_user)
    else:
        _video.like_count += 1
        await _video.like_user.add(_user)
    await _video.update()
    return _video.like_count