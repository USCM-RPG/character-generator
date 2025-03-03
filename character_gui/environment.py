#!/usr/bin/env python3

import os


exec_path = os.path.dirname(sys.executable)
if "USCM_CHARACTER_DIR" not in os.environ:
	os.environ["USCM_CHARACTER_DIR"] = os.path.join(exec_path, "player_characters")
	if not os.path.isdir(os.environ["USCM_CHARACTER_DIR"]):
		os.mkdir(os.environ["USCM_CHARACTER_DIR"])
	
if not "USCM_PDF_DIR" in os.environ:
	os.environ["USCM_PDF_DIR"] = os.path.join(exec_path, "exported_pdfs")
	if not os.path.isdir(os.environ["USCM_PDF_DIR"]):
		os.mkdir(os.environ["USCM_PDF_DIR"])