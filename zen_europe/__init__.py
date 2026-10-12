import pandas as pd

# Read .xlsx files with calamine rather than openpyxl. The raw data holds a few
# large workbooks, and openpyxl parses their XML in Python, which dominates the
# build. Call sites that need another reader can still pass `engine=`.
pd.options.io.excel.xlsx.reader = "calamine"
