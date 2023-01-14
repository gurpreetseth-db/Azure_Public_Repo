variable "spark_version" {
  type = string
}

variable "node_type_id" {
  type = string
}

variable "autotermination_minutes" {
  type    = number
  default = 60
}

variable "access_mode" {
  type = string
}

variable "single_user_access" {
  type = string
}

variable "keyvault_id" {
  type = string
}

variable "keyvault_url" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "clustername" {
  type = string
}