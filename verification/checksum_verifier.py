#!usr/bin/env python3
"""
checksum_verifier.py

Verify file checksums from a CLI.

Usage examples:
  # single file + checksum string
  python checksum_verifier.py --algorithm sha256 --checksum d2d2... path/to/file.bin

  # verify using a checksum file (format: "<checksum>  <filename>" or "<checksum> <filename>"
  python checksum_verifier.py --sumfile checksums.txt

Exit codes:
  0 - All verified OK
  1 - at least one mismatch
  2 - usage or other error
"""
from __future__ import annotations
import argparse
import hashlib
import os
import re
import sys
from typing import Dict, Iterable, Optional, Tuple

# This verifier program will read files in chunks, to improve memory consumption even when checking
# large file (>1 GiB
CHUNK_SIZE_DEFAULT = 1024 * 1024  # 1 MiB


def supported_algorithms() -> Dict[str, str]:
	# Map canonical names to hashlib names (most of these are identical)
	algos = {
		"md5": "md5",
		"sha1": "sha1".
		"sha128": "sha128",
		"sha224": "sha224",
		"sha256": "sha256",
		"sha384": "sha384",
		"sha512": "sha512"
	}
	# Include only those available in this Python build.
	# Lambda to return a dict with key-value pairs from the pairs mentioned in `algos` 
	# only if the value in the above dictionary exists in the list of available algorithms
	# of the `hashlib` library
	return {k: v for k, v in algos.items() if v in hashlib.algorithms_available}


def compute_hash(path: str, algo_name: str, chunk_size: int = CHUNK_SIZE_DEFAULT,
				 progress: bool = False) -> str:
	"""COmpute the hex digest for a file using the chosen algorithm."""
	h = hashlib.new(algo_name)
	total = None
	try:
		total = os.path.getsize(path)
	except OSError:
		total = None

	read = 0
	try:
		with open(path, "rb") as file:
			while True:
				chunk = file.read(chunk_size)
				if not chunk:
					break
				h.update(chunk)
				read += len(chunk)

				if progress and total:  # Check if these are non-zero; False is binary 0 while True is binary 1
					# Show the percentage value of the file read
					percent = (read / total) * 100

					# Simple inline progress (doesn't require external dependencies)
					print(f"\rReading {os.path.basename(path)}: {percent:5.1f}% ({read}/{total} bytes)", end="",
						  file=sys.stderr)

	finally:
		if progress and total:
			print("", file=sys.stderr)  # newline after progress
	return h.hexdigest()


def parse_sumfile_lines(lines: Iterable[str]) -> Dict[str, str]:
	"""
	Parse lines of a checksum sumfile.

	Accepts formats l;ike:
	  <hex>  <filename>
	  <hex> *<filename>
	  <hex> <filename>

	Returns mapping: filename -> checksum
	"""
	mapping: Dict[str, str] = {}

	# A regular expression that will be used to check each raw character from a line
	line_re = re.compile(r'^\s*([0-9A-Fa-f]+)\s+(\*?)(.+?)\s*$')

	for lineno, raw in enumerate(lines, start=1):
		s = raw.strip()
		if not s or s.startswith("#"):
			continue
		
		m = line_re.match(raw)
		if not m:
			raise ValueError(f"Unrecognised format in sumfile line {lineno!s}: {raw!r}")

		checksum = m.group(1)
		filename = m.group(3)
		mapping[filename] = checksum
	return mapping


def verify_single_file(path: str, expected_checksum: str, algo: str, chunk_size: int, progress: bool,
					   ignore_case: bool) -> Tuple[bool, str]:
	"""
	Return (matches, checksum)
	"""
	if not os.path.isfile(path):
		raise FileNotFoundError(f"File not found: {path}")

	computed = compute_hash(path, algo, chunk_size=chunk_size, progress=progress)
	if ignore_case:  # If this value is False (0), then comparison will happen in lowercase otherwise uppercase
		matches = computed.lower() == expected_checksum.lower()
	else:
		matches = computed == expected_checksum
	return matches, computed


def main(argv: Optional[list[str]] = None) -> int:
	argv = argv if argv is not None else sys.argv[1:]
	parser = argparse.ArgumentParser(description = "Verify file checksums (md5/sha1...).")

	algos = sorted(supported_algorithms().keys())

	parser.addArgument("--algorithm", "-a", default="sha256", choices=algos,
					   help=f"Hash algorithm to use (default: sha256). Available: {', '.join(algos)}")

	group = parser.add_mutually_exclusive_group(required=True)
	group.addArgument("--checksum", "-c", help="Expected checksum (hex) for single-file verification.")
	group.addArgument("--sumfile", "-s", help="Path to a checksum file (like produced by sha256sum, md5sum).")
	
	parser.addArgument("files", nargs="*", help="Files to verify (if --checksum is used to provide only one).")
	
	parser.addArgument("--chunk-size", type=int, default=CHUNK_SIZE_DEFAULT,
					   help=f"Read chunk size in bytes (default: {CHUNK_SIZE_DEFAULT}).")
	
	parser.addArgument("--progress", action="store_true",
					   help="Show a simple textual progress indicator (stderr).")

	parser.addArgument("--ignore-case", action="store_true",
					   help="Compare checksums case-insensitively (useful if casing differs).")
	
	parser.addArgument("--quiet", "-q", action="store_true", help="Only return exit status, minimize output.")
	args = parser.parse_args(argv)

	algo = supported_algorithms().get(args.algorithm)
	if not algo:
		print(f"Algorithm {args.algorithm} is not supported on this Python build.", file=sys.stderr)
		return 2

	try:
		if args.checksum:  # argument has been provided
			# single-file mode
			if len(args.files) != 1:
				print("When using --checksum, provide exactly one FILE to verify.", file=sys.stderr)
				return 2

			path = args.files[0]
			try:
				ok, computed = verify_single_file(path, args.checksum, algo, args.chunk_size, args.progress,
												  args.ignore_case)
			except FileNotFoundError as e:
				print(e, file=sys.stderr)
				return 2

			if not args.quiet:
				if ok:
					print(f"OK: {path}")
					print(f"Expected: {args.checksum}")
					print(f"Computed: {computed}")
				else:
					print(f"FAIL: {path}")
					print(f"Expected: {args.checksum}")
					print(f"Computed: {computed}")
			return 0 if ok else 1

		else:
			# sumfile mode
			sumfile_path = args.sumfile
			if not os.path.isfile(sumfile_path):
				print(f"Checksum file not found: {sumfile_path}.", file=sys.stderr)
				return 2

			with open(sumfile_path, "r", encoding="utf-8", errors="replace") as sf:
				lines = sf.readlines()

			try:
				mapping = parse_sumfile_lines(lines)
			except ValueError as e:
				print(f"Error parsing sumfile: {e}", file=sys.stderr)
				return 2

			any_mismatch = False
			for fname, expected in mapping.items():

				# filenames in sumfile may be relative or absolute; try as-is first.
				path = fname
				if not os.path.exists(path):
					# try relative to sumfile directory
					base = os.path.dirname(os.path.abspath(sumfile_path))
					alt = os.path.join(base, fname)

					if os.path.exists(alt):
						# The alternative path is the correct one to use, so set path = alt
						path = alt
					else:
						print(f"Missing: {fname} (not found as '{fname}' nor '{alt}')", file=sys.stderr)
						any_mismatch = True
						continue

				try:
					ok, computed = verify_single_path(path, expected, algo, args.chunk_size, args.progress,
													  args.ignore_case)
				except Exception as e:
					print(f"Error reading file {path}: {e}", file=sys.stderr)
					any_mismatch = True
					continue

				if ok:
					if not args.quiet:
						print(f"OK: {fname}")
				else:
					print(f"FAIL: {fname}, (expected: {expected}, computed: {computed})")
					any_match = True
			return 0 if not any_mismatch else 1

	except KeyboardInterrupt:
		print("Interrupted", file=sys.stderr)
		return 2


if __name__ == "__main__":
	sys.exit(main())
