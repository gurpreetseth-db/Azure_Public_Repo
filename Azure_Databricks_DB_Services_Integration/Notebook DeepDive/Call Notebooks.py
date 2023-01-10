# Databricks notebook source
# MAGIC %md <a href='$../Azure Integrations Start Here'>Home</a>

# COMMAND ----------

# MAGIC %md
# MAGIC ### With %run command we can call notebook from within a notebook cell.
# MAGIC Below example, we are calling a child1 notebook which resides in a seperte folder named children. 

# COMMAND ----------

# MAGIC %run ./children/child1

# COMMAND ----------

# MAGIC %md
# MAGIC #### We can print value from child1 notebook by refering t the variable that has been declraed in that notebook.

# COMMAND ----------

child1

# COMMAND ----------

# MAGIC %run ./children/child2

# COMMAND ----------

child2

# COMMAND ----------

# MAGIC %md
# MAGIC ### We can use dbutils function to run notebook. 
# MAGIC In below example, we are calling a notebook named Addition and passing 2 input values as Int and returing output hence creating a mini workflow.

# COMMAND ----------

x = 4
y = 2

z = dbutils.notebook.run('addition', 60, {'X': str(x), 'Y': str(y)})
print(z)
