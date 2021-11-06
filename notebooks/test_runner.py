# Databricks notebook source
# MAGIC %md
# MAGIC # Unit Test Runner
# MAGIC This notebook allows a test suite to be created for any registered tests.
# MAGIC 
# MAGIC To use this functionality, use the `%run` magic command to load the test notebook and then update the test suite.

# COMMAND ----------

dbutils.library.installPyPI('unittest-xml-reporting')
dbutils.library.restartPython()

# COMMAND ----------

import xml.etree.ElementTree as ET
import pandas as pd
import unittest
import xmlrunner
import uuid
import io
import datetime
import json

# COMMAND ----------

# MAGIC %run ./log_analytics_tests

# COMMAND ----------

# MAGIC %run ./more_tests

# COMMAND ----------

from inspect import getmro

def get_class_hierarchy(t):
  try:
    return getmro(t)
  except:
    return [object]

test_classes = {t for t in globals().values() if unittest.case.TestCase in get_class_hierarchy(t) and t != unittest.case.TestCase}
print(test_classes)

loader = unittest.TestLoader()
suite = unittest.TestSuite()
for test_class in test_classes:
  tests = loader.loadTestsFromTestCase(test_class)
  suite.addTests(tests)

out = io.BytesIO()
runner = xmlrunner.XMLTestRunner(out)
runner.run(suite)

# COMMAND ----------

out.seek(0)
test_results = ET.XML(out.read().decode('utf-8'))

ts = []
for suite in test_results:
  for test in suite:
    failures = [{k:v for k,v in failure.items()} for failure in test]
    if len(failures) > 0:
      for failure in failures:
        attributes = {k:v for k,v in suite.attrib.items()}
        attributes.update({f"test_{k}":v for k,v in test.attrib.items()})
        attributes.update({f"failure_{k}":v for k,v in failure.items()})
        ts.append(attributes)
    else:
      attributes = {k:v for k,v in suite.attrib.items()}
      attributes.update({f"test_{k}":v for k,v in test.attrib.items()})
      attributes.update({"failure_type":None, "failure_message":None})
      ts.append(attributes)
    
df = pd.DataFrame(ts)
df["tests"] = df["tests"].astype(int)
df["errors"] = df["errors"].astype(int)
df["failures"] = df["failures"].astype(int)
df["skipped"] = df["skipped"].astype(int)
df["succeeded"] = df["tests"] - (df["errors"] + df["failures"] + df["skipped"])
df = df.loc[:, ["timestamp", "name", "time", "tests", "succeeded", "errors", "failures", "skipped", "test_name", "test_time", "failure_type", "failure_message"]]
df

# COMMAND ----------

idx = df.groupby(["name", "tests", "succeeded", "errors", "failures", "skipped"]).first().index
columns = idx.name

gf = pd.DataFrame([[x for x in t] for t in idx], columns=idx.names)
gf.index = gf["name"]
gf = gf.iloc[:,2:]
gf.T.plot.pie(subplots=True, colors=['green', 'red', 'red', 'yellow'], labeldistance=None, figsize=(8,8))

# COMMAND ----------

out.seek(0)
dbutils.notebook.exit(out.read().decode('utf-8'))
