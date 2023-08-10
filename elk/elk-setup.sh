#/bin/sh
echo "Waiting for Elasticsearch availability";
until curl http://ov2xmp-elasticsearch:9200 | grep -q "missing authentication credentials"; do sleep 30; done;
echo "Setting kibana_system password";
until curl -X POST -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" http://ov2xmp-elasticsearch:9200/_security/user/kibana_system/_password -d "{\"password\":\"${KIBANA_PASSWORD}\"}" | grep -q "^{}"; do sleep 10; done;
echo "All done!";

exit 0;