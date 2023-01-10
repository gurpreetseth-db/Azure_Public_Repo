# Databricks notebook source
import sys
import os
sys.path.append(os.path.abspath('Workspace/Repos/'+dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()+'Azure Integrations Start Here/datasets'))


# COMMAND ----------

# MAGIC %fs ls /Workspace/

# COMMAND ----------

print(os.path.abspath)

# COMMAND ----------

dbutils.fs.mkdirs('/Users/'+dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()+'/datasets')

# COMMAND ----------

print(sys.path)

# COMMAND ----------

dbutils.fs.cp('/*', '/Users/'+dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()+'/datasets/')

# COMMAND ----------

dbutils.fs.ls("/Workspace/")
