# es_liberare_py An Elastic Search Bulk Data Dumper in Bash and Python

### Usage:
```bash
chmod a+x bulk_dump.sh
./bulk_dump.sh $HOST $INDEX
```

### Output:

#### Index Definition File

One file named `create_index--$HOST--$INDEX.idx.json` will be created 
which is derived from the output of the command `http://'$HOST':9200/'$INDEX'/_settings,_mapping/?pretty` 
and which can be passed directly back to the target Elasticsearch server to re-create the index definition:
```
curl -XPOST http://$TARGETHOST:9200/$INDEX -d @$HOST--$INDEX.create_index.json
```

#### Many Bulk Dump Files

Multiple bulk dump files per document type are created.  Each file contains up to 1000 entries
from the original index.

#### CAUTIONs

**!Please Add to this list as issues arrise:**

1. The index definition can contain implicit references to plug-ins.  Plugins should be checked on the target system before re-ingesting data.

#### References:

1. [https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html)
2. [https://qbox.io/blog/building-an-elasticsearch-index-with-python](https://qbox.io/blog/building-an-elasticsearch-index-with-python)
3. [https://sarahleejane.github.io/learning/python/2015/10/14/creating-an-elastic-search-index-with-python.html](https://sarahleejane.github.io/learning/python/2015/10/14/creating-an-elastic-search-index-with-python.html)


