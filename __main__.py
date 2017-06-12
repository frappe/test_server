from github import Github
import os, sys, time
import subprocess
import click
import json

allowed_domains = ('Manufacturing', 'Education')

# TODO

with open('test_server/config.json', 'r') as f:
	conf = json.loads(f.read())
	g = Github(conf['user'], conf['password'])

@click.group()
def cli():
	pass

@cli.command()
@click.option('--app', help='Make for app, if not specified will make for both frappe and erpnext')
def make(app=None):
	if app:
		make_for(app)
	else:
		make_for('frappe')
		make_for('erpnext')

	restart()

def make_for(app):
	repo = g.get_user('frappe').get_repo(app)
	app_path = os.path.join('apps', app)
	print 'Fetching {0}...'.format(app)

	subprocess.check_output(['git', 'fetch', 'upstream'], cwd = app_path)

	all_sites = []

	for p in repo.get_pulls().reversed:
		site = '{0}-{1}.erpnext.xyz'.format(app[0], p.number)
		all_sites.append(site)
		
		switch_to_base_branch(p.base.ref)

		if os.path.exists(os.path.join('sites', site)):
			update_and_migrate(p, site, app_path)
		else:
			setup_pull(p, site, app_path)

	delete_closed(app)

def setup_pull(p, site, app_path):
	checkout(p, site, app_path)
	pull(p, app_path)
	make_site(site)
	run_demo(site)
	add_base_ref_flag(site, p.base.ref)

def switch_to_base_branch(branch):
	for app in ('frappe', 'erpnext'):
		try:
			subprocess.check_output(['git', 'checkout', branch], cwd=os.path.join('apps', app))
		except:
			subprocess.check_output(['git', 'checkout', '-b', branch, 'upstream/{0}'.format(branch)], 
				cwd=os.path.join('apps', app))

def add_base_ref_flag(site, branch):
	with open(os.path.join('sites', site, '.baseref'), 'w') as f:
		f.write(branch)

def update_and_migrate(p, site, app_path):
	# get the branch
	print 'Updating and migrating {0}...'.format(site)
	try:
		subprocess.check_output(['git', 'checkout', site], cwd=app_path)
	except:
		# bad site
		drop_site(site, app_path)
		setup_pull(p, site, app_path)
		return

	pull(p, app_path)
	subprocess.check_output(['bench', '--site', site, 'migrate'])
	add_base_ref_flag(site, p.base.ref)

def checkout(p, site, app_path):
	# get the branch
	try:
		# try deleting the old branch
		subprocess.check_output(['git', 'branch', '-D', site], cwd=app_path)
	except:
		pass

	subprocess.check_output(['git', 'checkout', '-b', site, 
		p.base.ref], cwd = app_path)


def pull(p, app_path):
	# pull the patch
	if p.head.repo:
		subprocess.check_output(['git', 'pull', p.head.repo.html_url + '.git',
			p.head.ref], cwd = app_path)
	else:
		try:
			# apply directly
			subprocess.check_call(['curl', '-L', p.patch_url, '|', 'git', 'am', '-3'],
				cwd = app_path, shell=True)
		except:
			print 'Failed. Bad Pull Request {0}'.format(p.html_url)
			sys.exit(1)


def make_site(site):
	print 'Creating {0}...'.format(site)
	subprocess.check_output(['bench', 'new-site', site], cwd='.')

	print 'Installing erpnext...'
	subprocess.check_output(['bench', '--site', site, 'install-app', 
		'erpnext'], cwd='.')

def run_demo(site, p):
	print 'Running demo for 3 days...'
	try:
		domain = 'Manufacturing'
		if '\ndemo-domain:' in pull.body:
			_domain = pull.body.split('\ndemo-domain:')[1].split('\n')[0].strip()
			if _domain in allowed_domains:
				domain = _domain
		subprocess.check_output(['bench', '--site', site, 'make-demo', '--days', '3', 
			'--demo', domain])

		# add a breather for mysql (?)
		time.sleep(3)
	except:
		print 'Unable to run demo'

def delete_closed(app):
	# delete sites for closed PRs
	print '-' * 20
	print 'Cleaning up...'

	for site in os.listdir('sites'):
		if (os.path.isdir(os.path.join('sites', site)) 
			and site.startswith(app[0] + '-') 
			and site not in all_sites):

			drop_site(site, os.path.join('apps', app))

def drop_site(site, app_path):
	print 'Dropping {0}...'.format(site)
	subprocess.check_output(['bench', 'drop-site', site]) 

	print 'Deleting branch {0}...'.format(site)	
	try:
		# try deleting the old branch
		subprocess.check_output(['git', 'branch', '-D', site], 
			cwd=app_path)
	except:
		pass

@cli.command()
@click.option('--site', help='switch to site')
def use(site):
	with open(os.path.join('sites', site, '.baseref'), 'r') as f:
		base_ref = f.read()
		
	if site.startswith('f-'):
		subprocess.check_output(['git', 'checkout', baseref], cwd='apps/erpnext')
		subprocess.check_output(['git', 'checkout', site], cwd='apps/frappe')
	else:
		subprocess.check_output(['git', 'checkout', baseref], cwd='apps/frappe')
		subprocess.check_output(['git', 'checkout', site], cwd='apps/erpnext')
	subprocess.check_output(['bench', 'restart'])

@cli.command()
def restart():
	print 'Relading supervisor and nginx'
	subprocess.check_output(['sudo', 'bench', 'setup', 'supervisor', '--yes'])
	subprocess.check_output(['sudo', 'bench', 'setup', 'nginx', '--yes'])
	subprocess.check_output(['sudo', 'supervisorctl', 'reread'])
	subprocess.check_output(['sudo', 'supervisorctl', 'update'])
	subprocess.check_output(['sudo', 'service', 'nginx', 'reload'])


if __name__=='__main__':
	cli()
