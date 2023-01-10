# Databricks notebook source
# MAGIC %md <a href='$../Azure Integrations Start Here'>Home</a>

# COMMAND ----------

# MAGIC %md
# MAGIC # Git Integration and Collaboration!
# MAGIC 
# MAGIC Databricks Repos is a visual Git client in Databricks. It supports common Git operations such a cloning a repository, committing and pushing, pulling, branch management, and visual comparison of diffs when committing.
# MAGIC 
# MAGIC Within Repos you can develop code in notebooks or other files and follow data science and engineering code development best practices using Git for version control, collaboration, and CI/CD.
# MAGIC 
# MAGIC https://learn.microsoft.com/en-us/azure/databricks/repos/

# COMMAND ----------

# MAGIC %md
# MAGIC #### What can you do with Databricks Repos?
# MAGIC Databricks Repos provides source control for data and AI projects by integrating with Git providers.
# MAGIC 
# MAGIC In Databricks Repos, you can use Git functionality to:
# MAGIC 
# MAGIC * Clone, push to, and pull from a remote Git repository.
# MAGIC * Create and manage branches for development work.
# MAGIC * Create notebooks, and edit notebooks and other files.
# MAGIC * Visually compare differences upon commit.

# COMMAND ----------

# MAGIC %md
# MAGIC #### Add a repo
# MAGIC To create a new repo not linked to a remote Git repository, click the Add Repo button. Deselect Create repo by cloning a Git repository, enter a name for the repo, and then click Create Repo.

# COMMAND ----------

# MAGIC 
# MAGIC %md
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/connect-repo-later.png?raw=true" />
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/repo-menu.png?raw=true" />
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/git-dialog-settings.png?raw=true" />

# COMMAND ----------

# MAGIC %md
# MAGIC #### Add a repo connected to a remote repo (repo already exists in Git or AzureDevops etc)

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/add-repo.png?raw=true" />
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC &nbsp;
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/clone-from-repo.png?raw=true" />

# COMMAND ----------

# MAGIC %md
# MAGIC ####Access the Git dialog
# MAGIC You can access the Git dialog from a notebook or from the Databricks Repos browser.

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/notebooks/toolbar.png?raw=true" />
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/git-button-repos.png?raw=true" />
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/repo-menu.png?raw=true" />

# COMMAND ----------

# MAGIC %md
# MAGIC ####Resolve merge conflict
# MAGIC To resolve a merge conflict, you must either discard conflicting changes or commit your changes to a new branch and then merge them into the original feature branch using a pull request.

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/resolve-conflict-dialog.png?raw=true" />
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC &nbsp;
# MAGIC 
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/merge-conflict-create-pr-msg.png?raw=true" />

# COMMAND ----------

# MAGIC %md
# MAGIC #### Commit and push changes to the remote Git repository
# MAGIC When you have added new notebooks or files, or made changes to existing notebooks or files, the Git dialog highlights the changes.

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://learn.microsoft.com/en-us/azure/databricks/_static/images/repos/git-commit-push.png?raw=true" />

# COMMAND ----------

# MAGIC %md
# MAGIC To know more about Git operations, please refer https://learn.microsoft.com/en-us/azure/databricks/repos/git-operations-with-repos
