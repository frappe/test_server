from github import Github
import json, subprocess, os

_github = None

def get_github():
	global _github

	if not _github:
		conf = get_conf()
		_github = Github(conf['user'], conf['password'])

	return _github

def get_conf():
	with open('test_server/config.json', 'r') as f:
		conf = json.loads(f.read())

	return conf

def get_baseref(site):
    with open(os.path.join('sites', site, '.baseref'), 'r') as f:
        baseref = f.read()

    return baseref

def _restart():
	print 'Relading supervisor and nginx'
	subprocess.check_output(['sudo', 'bench', 'setup', 'supervisor', '--yes'])
	subprocess.check_output(['sudo', 'bench', 'setup', 'nginx', '--yes'])
	subprocess.check_output(['sudo', 'supervisorctl', 'reread'])
	subprocess.check_output(['sudo', 'supervisorctl', 'update'])
	subprocess.check_output(['sudo', 'service', 'nginx', 'reload'])

