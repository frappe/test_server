import os
import subprocess
import click
import json

from make import make_for, delete_closed
from utils import _restart, get_baseref
from review import _review

@click.group()
def cli():
	pass

@cli.command()
@click.option('--app', help='Make for app, if not specified will make for both frappe and erpnext')
@click.option('--restart', is_flag=True, default=False, help='Rebuild all sites')
def make(app=None, restart=False):
	completed_sites = []
	all_sites = []
	if restart:
		if os.path.exists('.completed_sites'):
			os.remove('.completed_sites')
	else:
		if os.path.exists('.completed_sites'):
			with open('.completed_sites', 'r') as f:
				completed_sites = json.loads(f.read())
	if app:
		make_for(app, completed_sites)
	else:
		all_sites = make_for('frappe', completed_sites)
		all_sites += make_for('erpnext', completed_sites)

	delete_closed(all_sites)
	os.remove('.completed_sites')
	_restart()

@cli.command()
@click.option('--site', help='Update and switch to site')
def use(site):
    if not site.endswith('.erpnext.xyz'):
        site += '.erpnext.xyz'
    app = 'erpnext' if site.startswith('e') else 'frappe'
    other = 'erpnext' if app=='frappe' else 'frappe'
    baseref = get_baseref(site)

    # for app
    subprocess.check_output(['git', 'checkout', site], cwd=os.path.join('apps', app))
    subprocess.check_output(['git', 'pull', '--rebase', 'upstream', baseref],
        cwd=os.path.join('apps', app))

    # for other
    subprocess.check_output(['git', 'checkout', baseref], cwd=os.path.join('apps', other))
    subprocess.check_output(['git', 'pull', 'upstream', baseref], cwd=os.path.join('apps', other))

    subprocess.check_output(['bench', '--site', site, 'migrate'])

    subprocess.check_output(['bench', 'build'])
    subprocess.check_output(['bench', 'restart'])

@cli.command()
def restart():
	_restart()

@cli.command()
@click.option('--pull', default=None, help='Pull Request to Review, e.g. f-2111')
def review(pull=None):
	_review(pull)

if __name__=='__main__':
	cli()