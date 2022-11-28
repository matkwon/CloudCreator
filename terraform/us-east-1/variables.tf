variable "vpc" {
  type = object({
    cidr_block = string
    tags       = map(string)
    active     = bool
  })
  description = "VPC configuration"
}

variable "subnets" {
  type = list(object({
    cidr_block = string
    tags       = map(string)
  }))
  description = "Subnets configuration"
}

variable "instances" {
  type = list(object({
    instance_type = string
    nic           = string
    tags          = map(string)
  }))
  description = "Instances configuration"
}

variable "network_interfaces" {
  type = list(object({
    subnet          = string
    private_ips     = list(string)
    security_groups = list(string)
    tags            = map(string)
  }))
  description = "Network interfaces configuration"
}

variable "security_groups" {
  type = list(object({
    name        = string
    description = string
    ports       = list(object({
      from = number
      to   = number
    }))
  }))
  description = "Security group for Transport Layer Security"
}

variable "users" {
  type        = list(string)
  description = "Usernames"
}