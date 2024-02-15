# модуль для кастомных функций,которые будут использованы в приложении
from github import Github,GithubException
from datetime import datetime,timedelta

# Получаем топ-100 репозиториев по звездам с GitHub
def get_top_repositories(git_token):
    
    g = Github(git_token)

    # Запрос репозиториев без сортировки
    repositories = g.search_repositories(query='stars:>0')[:100]

    # Составление списка словарей с информацией о репозиториях
    top_repos_list = []
    for repo in repositories:
        repo_info = {
            'name': repo.name,
            'owner': repo.owner,
            'stars': repo.stargazers_count,
            'watchers': repo.subscribers_count,
            'forks': repo.forks_count,
            'open_issues': repo.open_issues_count,
            'lang': repo.language,
        }
        top_repos_list.append(repo_info)

    for repo in top_repos_list:
        repo['owner'] = repo['owner'].login if repo['owner'] is not None else None

    return top_repos_list



def get_repository_activity(git_token, owner, repo, since, until):
    try:
        g = Github(git_token)
        repository = g.get_repo(f"{owner}/{repo}")

        # Преобразуем since и until в объекты datetime
        since_date = datetime.combine(since, datetime.min.time())
        until_date = datetime.combine(until + timedelta(days=1), datetime.min.time())

        commits = repository.get_commits(since=since_date, until=until_date)  # Получаем коммиты за указанный промежуток времени
        activity_data = {}

        # Обрабатываем каждый коммит
        for commit in commits:
            commit_date = commit.commit.author.date.date()

            if since <= commit_date <= until:
                if commit_date not in activity_data:
                    activity_data[commit_date] = {"commits": 1, "authors": set([commit.author.login])}
                else:
                    activity_data[commit_date]["commits"] += 1
                    activity_data[commit_date]["authors"].add(commit.author.login)

        # Преобразуем словарь в список объектов ActivityItem
        result_data = []
        for commit_date, data in activity_data.items():
            result_data.append({
                "date": commit_date,
                "commits": data["commits"],
                "authors": list(data["authors"]),
            })

        return result_data

    except GithubException as e:
        # Обработка ошибок, связанных с GitHub API
        print(f"GitHub API error: {e}")
        return []
    except Exception as e:
        # Обработка других исключений
        print(f"An unexpected error occurred: {e}")
        return []
