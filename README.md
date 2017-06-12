### Test Server Setup Utility

This utility sets up the test server for testing pull requests on frappe and erpnext

- It will create a new site for each Pull Request
- If the site exists, it will pull the latest patch and run migrate
- The site name will be the pull number with a prefix `e` for erpnext and `f` for frappe. Example `e-9872.erpnext.xyz`
- A branch will be created for each site
- The branch for the other repo will be the base branch of the pull-request (hotfix or develop)
- It will delete all sites, branches not on current pull request


#### Sending Pull Requests

You can configure pull requests by adding a few commands / keys in the pull request body

- If you want to run a demo for another domain (like Education), add a line in the pull request body whic is like `demo-domain: Education`
- If the pull request in ERPNext is dependant on a Frappe PR, add the word "depends" and the url to the frappe pull request

Example:

```
depends on: https://github.com/frappe/frappe/pull/1111
demo-domain: Education
```

### Usage

```
cd frappe-bench

# make sites
python test_server make

# swtch sites
python test_server use --site f-2332.erpnext.xyz
```

#### Resuming make

If the make function breaks, you might have to manually see why the site is not installing. If you run `make` again it will continue by default from the site that broke. To restart running all sites again, run `python test_server make --restart`


