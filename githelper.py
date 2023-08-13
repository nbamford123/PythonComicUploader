from git import Repo


def publish_comic(repo_dir, chapter, page):
    existing_repo = Repo(repo_dir)
    new_branch = f'publish-{chapter}-{page}'
    current = existing_repo.create_head(new_branch)
    print(f'Branch publish-{chapter}-{page} created')
    current.checkout()
    print(f'Branch publish-{chapter}-{page} checked out')
    master = existing_repo.heads.master
    existing_repo.git.pull('origin', master)
    existing_repo.git.add('*')
    existing_repo.git.commit(m=f'Publishing {chapter}-{page}')
    print(f'Branch publish-{chapter}-{page} committed')
    existing_repo.git.push('--set-upstream', 'origin', new_branch)
    print(f'Branch publish-{chapter}-{page} pushed')
    master.checkout()
    print(f'Checking out master')
