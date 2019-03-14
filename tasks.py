from invoke import task

@task
def clean(c, docs=True, bytecode=True):
    patterns = ['build', 'dist', 'pymitter.egg-info']
    if docs:
        patterns.append('build/docs')
    if bytecode:
        patterns.append('**/*.pyc')
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))

@task
def docs(c, host=False):
    c.run("sphinx-apidoc -o docs ./pyvent -f")
    c.run("sphinx-build docs build/docs")

    if host:
        c.run("cd docs/_build && python3 -m http.server 8080")

@task
def build(c):
    c.run("python setup.py bdist_wheel")
