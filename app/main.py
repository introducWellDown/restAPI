from fastapi import FastAPI, Query, Request,Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from function import get_repository_activity
from datetime import date
from threading import Thread
from structure import ActivityItem
from DB import conn,export_repositories
import os
import dotenv
from trigger import update_DB
dotenv.load_dotenv()


git_token = os.environ.get("git_token")
app = FastAPI()
templates = Jinja2Templates(directory="../templates")

# Запускаем обновление данных В ДБ
update_thread = Thread(target=update_DB, args=(conn, 60))
update_thread.daemon = True  # Поток завершится, когда основной поток завершится
update_thread.start()

# Первый эндпоинт для топа
@app.get("/api/repos/top100", response_class=HTMLResponse)
async def get_top100_repositories(
    request: Request,
    sort: str = Query('stars', description="Sort by 'stars', 'watchers', 'forks', 'open_issues','language"),
):
    top_repos_tuples = export_repositories(conn, sort)
    top_repos_dicts = [{'name': repo[1], 'owner': repo[2], 'stars': repo[3],
                        'watchers': repo[4], 'forks': repo[5], 'open_issues': repo[6], 'lang': repo[7]}
                       for repo in top_repos_tuples]
    top_repos = [
        {'position': i + 1, **repo}
        for i, repo in enumerate(top_repos_dicts)
    ]
    return templates.TemplateResponse("top100.html", {"request": request, "top_repos": top_repos})
# Второй эндпоинт для конкретного репозитория 


    
@app.get("/api/repos/{owner}/{repo}/activity", response_model=list[ActivityItem])
async def post_repository_activity(
    request: Request,
    owner: str = Path(..., title="Владелец репозитория"),
    repo: str = Path(..., title="Название репозитория"),
    since: date = Query(..., title="Начальная дата", description="Format: YYYY-MM-DD"),
    until: date = Query(..., title="Конечная дата", description="Format: YYYY-MM-DD"),
):
    activity_data = get_repository_activity(git_token, owner, repo, since, until)
    return templates.TemplateResponse("info.html", {"request": request,"activity_data": activity_data,
                                                    "owner": owner,"repo": repo,"since": since,"until": until}) 
    