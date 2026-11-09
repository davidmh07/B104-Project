import numpy as nm
import matplotlib.pyplot as plt
import pandas as pd
from mdb_parser import MDBParser

# Team: Frankie Sacco/David Heitman
# Team: 4
# Course: B104
# This project aims to explore the correlation between youth mental health and the role
# and impact it has on drug habits, such as alcohol/nicotine intake.

# For now, just attempting to load .mdb file into Python:

db_path = r"C:\Users\fsacco\Downloads\XXH2025_YRBS_Data.mdb"
parser = MDBParser(db_path)

print("Tables: ", parser.tables)



