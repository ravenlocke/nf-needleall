# Needleall

This is a workflow for running needleall to use a query FASTA file to search for hits in a DB file. 

## Calling the workflow
This workflow can be called like so:

```
nextflow run ravenlocke/nf-needleall --query {query_file.fasta} --db {database.fasta} --threshold {T} --outroot {root}
```

This will find hits in the DB with FASTA records in the query, which are then written out to a file in the directory from which you ran the command, named `{root}_identities.txt`. `--threhold {T}` can be omitted (which will return all hits with some identity), but if given then only hits with an identity >= `{T}` are returned.
