###  Pull Request Summary

{% if not props.has_image and not props.has_gif %}
#### Image or animted GIF Not Added

Please add an image or animated GIF as proof that you have manually tested this contribution. Hint: use [LiceCAP](http://www.cockos.com/licecap/) to capture animated GIFs.
{% endif %}
{% if props.py_changed and not props.test_py_changed %}
#### Test Case Not Added / Updated

Since you have changed a Python file, you must update the relevant python test case. If there is no test coverage for this code, then please add it.
{% endif %}
{% if props.new_doctype and not props.py_test_added %}
#### New DocType does have a test

Since you have created a new DocType, please add at least one test case.
{% endif %}
{% if props.code_changes > 50 and props.code_changes < 100 %}
#### Try Fewer Changes

This is a midsized pull request, try changing only 50 lines in a go next time.
{% endif %}
{% if props.code_changes > 100 %}
#### Large Patch

This is a very large pull request, unless there is a very good reason, please try and break it down to smaller changes. [Read this strategy on how it can be done](https://github.com/frappe/erpnext/wiki/Cascading-Pull-Requests)
{% endif %}
{% if props.has_cur_frm %}
#### Please use modern JS API for forms

`cur_frm` is now deprecated and your patch contains code edited with `cur_frm`. Please re-write this code so that there are no references to `cur_frm` in your patch.
{% endif %}
{% if props.doctype_changed and not props.docs_changed %}
#### Documentation not updated

Since you have changed a DocType, check if this impacts any of the documentation related to it.
{% endif %}
{% if props.doctype_changed and not props.demo_changed and props.code_changes > 100 %}
#### Demo not Updated

Since this is a large pull request, check if the demo is changed / updated
{% endif %}

---

### Result

{% if not props.has_image and props.js_changed %}- **Failed:** User testing is mandatory for patches with changes in JS code. {% endif %}
{% if props.code_changes > 100 and not props.test_py_changed %}- **Failed:** Updating test cases is mandatory for large pull requests{% endif %}
{% if not props.has_gif and props.code_changes > 100 %}- **Failed:** User testing with animated GIF is mandatory for large pull requests. {% endif %}
{% if props.has_cur_frm %}- **Failed:** `cur_frm` is used{% endif %}
{% if props.code_changes < 50 %}- **Passed:** Small Pull Request{% endif %}
{% if props.doctype_added and not props.docs_changed %}- **Failed: ** No documentation for new DocType{% endif %}

---

This summary was automatically generated [based on this script](https://github.com/frappe/test_server)