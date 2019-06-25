#!/usr/bin/env python

import os as _os
import subprocess as _sp
import tempfile as _tf
import multiprocessing as _mp
import uuid as _uuid

from Bio import SeqIO as _sqio

_NEWLINE = """
"""

def set_global_lock(l):
	global lock
	lock = l

class NeedleAll():
	def __init__(self, outfile, gap_open_penalty=10, gap_extend_penalty=0.5, threshold=-1):
		self.outfile = outfile
		if _os.path.isfile(self.outfile):
			raise Exception("Outfile given already exists, please choose a new location")
		self.gap_open_penalty = gap_open_penalty
		self.gap_extend_penalty = gap_extend_penalty
		self.record_id_map = {}
		self.threshold = threshold

	def run(self, query, db):
		with _tf.NamedTemporaryFile() as aseq, \
			_tf.NamedTemporaryFile() as bseq, \
			_tf.NamedTemporaryFile(suffix='.needleout') as needleout:

			# Write to temporary files using shorter names.
			counter = 0
			for record in _sqio.parse(query, 'fasta'):
				new_id = f'R{counter}'
				self.record_id_map[new_id] = record.id
				record.id = new_id
				aseq.write(record.format('fasta').encode())
				aseq.seek(0,2)
				counter += 1

			for record in _sqio.parse(db, 'fasta'):
				new_id = f'R{counter}'
				self.record_id_map[new_id] = record.id
				record.id = new_id
				bseq.write(record.format('fasta').encode())
				bseq.seek(0,2)
				counter += 1				

			aseq.seek(0)
			bseq.seek(0)

			# Generate the command and run needleall
			command = ['needleall',	'-asequence', aseq.name, '-bsequence', bseq.name,
				'-gapopen', f'{self.gap_open_penalty}', '-gapextend',f'{self.gap_extend_penalty}',
				'-outfile', needleout.name, '-aformat3', 'pair']
			# Run needleall
			p = _sp.Popen(command, stdout=_sp.PIPE, stderr=_sp.PIPE)
			stdout, stderr = p.communicate()

			# Vector to hold identities.
			identities = []
			# Parse the results file
			with open(needleout.name, 'r') as f:
				id1, id2, identity = None, None, None
				for line in f:
					if line.strip().startswith('# 1:'):
						id1 = line.strip().split()[2]

					if line.strip().startswith('# 2:'):
						id2 = line.strip().split()[2]

					if line.strip().startswith('# Identity'):
						num, den = line.strip().split()[2].split('/')
						num, den = int(num), int(den)
						identity = num / den
						identities.append((id1, id2, identity,))

						# Reset variables so that any future iterations don't use these.
						num, den, identity, id1, id2 = None, None, None, None, None

			# Write to file.
			with open(self.outfile, 'w') as f:
				for id1, id2, identity in identities:
					if not identity > self.threshold:
						continue
					f.write(f"{identity} {self.record_id_map[id1]} {self.record_id_map[id2]}{_NEWLINE}")



rid = _uuid.uuid4()
A = NeedleAll(f"{rid}-identities.txt", threshold=${params.threshold})
A.run("${query.name}", "${db_frag.name}")
