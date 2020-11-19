PLUGIN_VERSION=1.0.0
PLUGIN_ID=jira

plugin:
	cat plugin.json|json_pp > /dev/null
	rm -rf dist
	mkdir dist
	zip --exclude "*.pyc" -r dist/dss-plugin-${PLUGIN_ID}-${PLUGIN_VERSION}.zip custom-recipes parameter-sets python-lib python-connectors plugin.json
