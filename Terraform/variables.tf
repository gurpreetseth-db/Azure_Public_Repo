# First Two Variables are used for Tagging and Naming resources

variable "name"{
  type = string
  default = "Gurpreet Sethi"
}

variable "email"{
  type = string
  default = "gurpreet.sethi@databricks.com"
}



# Azure Region Where Resources Will Be Deployed

variable "rglocation" {
  type    = string
  default = "australiasoutheast"
}


# Type of Cluster That Will Gets Created Once Databricks Workspace Gets Provisioned
variable "node_type" {
  type = string
  default = "Standard_DS3_v2"
}

# Number of Mins post which Cluster Will be Terminated

variable "global_auto_termination_minute" {
  type    = number
  default = 30
}

variable "no_public_ip" {
  type    = bool
  default = false
}
