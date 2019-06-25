#!/usr/bin/env nextflow

params.query = null
params.db = null
params.outroot = null
params.threshold = -1

/*
Check that the relevant parameters are present to carry out the assembly
*/

// Checking whether the user has indicated an infile and outfile
if (params.query == null){
	error "--infile is a required parameter (the FASTA file containing query for identity calculations)"
} else {
	query = file( params.query )
}

if (params.db == null){
	error "--db is a required parameter (the FASTA file containing the database to be searched)"
} else {
	db = file( params.db ) 
}

if (params.outroot == null){
	error "--outroot is a required parameter (the name of the directory to store results)"
} 


/*
Run the Nextflow workflow
*/


// This process exposes the forward and reverse reads to the rest of the workflow.
process exposeData {
	output:
	file "query.fasta" into calculate_identity
	file "db.fasta" into fragment_db

	script:
	"""
	ln -s $query query.fasta
	ln -s $db db.fasta
	"""
}

fragmented_db = fragment_db
	.splitFasta(by: 100, file: true)


process needleall {
	container "ravenlocke/emboss:6.6.0"
	input:
	file query from calculate_identity
	file db_frag from fragmented_db

	output:
	file "*-identities.txt" into tmp

	script:
	template "needleall.py"

}

to_sort = tmp.collectFile(name: "$TMPDIR/results.txt")


process sort {

	publishDir "${workflow.launchDir}", mode: "copy"

	input:
	file to_sort

	output:
	file "${params.outroot}_identities.txt" into outfile

	script:
	"""
	sort -r -n -k 1 ${to_sort} > ${params.outroot}_identities.txt 
	"""
}