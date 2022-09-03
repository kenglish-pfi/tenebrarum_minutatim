DROP TABLE IF EXISTS kenglish.torcrawl_http;
CREATE EXTERNAL TABLE kenglish.torcrawl_http (
    code STRING,
    url STRING,
    response STRING
)
STORED AS PARQUET
LOCATION '/user/kenglish/proj/dhs/census_dept_2020-02feb/tor_httpscan_output';