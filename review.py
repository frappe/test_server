from utils import get_github, get_conf
import jinja2, re

def _review(number=None):
	if not number:
		for app in ('frappe', 'erpnext'):
			for pull in get_github().get_user('frappe').get_repo(app).get_pulls().reversed:
				pull_review(pull, app)

	else:
		pull_review(number)

def pull_review(pull, app=None):
	'''Review pull request'''
	conf = get_conf()
	if isinstance(pull, basestring):
		app = 'erpnext' if pull.startswith('e') else 'frappe'
		pull = get_github().get_user('frappe').get_repo(app).get_pull(int(pull[2:]))

	issue = get_github().get_user('frappe').get_repo(app).get_issue(pull.number)

	if already_commented(conf, pull, issue):
		# already commented on this PR
		print 'Already commented on {0}'.format(pull.number)
		return

	props = get_pr_props(pull, issue, app)

	env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath='test_server'))
	body = env.get_template('recommendation.md').render(dict(props=props))

	# add comment to pull-request
	issue.create_comment(body=body)

def already_commented(conf, pull, issue):
#	my_last_comment_at = False
	for comment in issue.get_comments():
		if comment.user.login == conf['user']:
#			my_last_comment_at = comment.updated_at

			return True

	# commits = pull.get_commits()
	# diff = (parser.parse(commits[0].last_modified)
	# 	- pytz.utc.localize(my_last_comment_at)).seconds
	#
	# if my_last_comment_at and diff < 60:
	# 	return True

	return False

def get_pr_props(pull, issue, app):
	props = {}

	def check_for_images(body):
		if re.search('https://cloud.githubusercontent.com[^ ]*png', body):
			props['has_image'] = 1

		if re.search('https://cloud.githubusercontent.com[^ ]*gif', body):
			props['has_gif'] = 1


	code_changes = 0

	for f in pull.get_files():
		if f.filename.endswith('.py'):
			if f.filename.startswith('test_'):
				props['test_py_changed'] = 1
			props['py_changed'] = 1
			code_changes += f.changes

			if app=='erpnext' and '/demo/' in f.filename:
				props['demo_changed'] = 1

		if f.filename.endswith('.json'):
			props['doctype_changed'] = 1
			if f.status=='added':
				props['new_doctype'] = 1
		if f.filename.endswith('.js'):
			props['js_changed'] = 1
			code_changes += f.changes
			if 'cur_frm' in f.patch or "":
				props['has_cur_frm'] = 1

		if f.filename.endswith('.md') or ('/docs/' in f.filename):
			props['docs_changed'] = 1

		check_for_images(pull.body or "")

	# check comments for images
	if not props.get('has_gif') or not props.get('has_image'):
		for comment in issue.get_comments():
			check_for_images(comment.body or "")

	props['code_changes'] = code_changes

	return props