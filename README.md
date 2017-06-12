### Test Server Setup Utility

This utility sets up the test server for testing pull requests on frappe and erpnext

- It will create a new site for each Pull Request
- The site name will be the pull number with a prefix `e` for erpnext and `f` for frappe
- A branch will be created for each site
- The branch for the other repo will be the base branch of the pull-request (hotfix or develop)
- It will delete all sites, branches not on current pull request

### Usage

```
cd frappe-bench

# make sites
python test_server make

# swtch sites
python test_server use --site f-2332.erpnext.xyz
```

