variable "region" {
  type        = string
  description = "AWS region"
}

variable "vpc" {
  type = object({
    cidr_block = string
    tags       = map(string)
  })
  description = "VPC configuration"
}

variable "subnets" {
  type = list(object({
    cidr_block        = string
    availability_zone = string
    tags              = map(string)
  }))
  description = "Subnets configuration"
}

variable "instances" {
  type = list(object({
    ami           = string
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
    device          = string
    tags            = map(string)
  }))
  description = "Network interfaces configuration"
}

variable "security_groups" {
  type = list(object({
    name        = string
    description = string
  }))
  description = "Security group for Transport Layer Security"
}

variable "rules" {
  type = list(object({
    from_port = number
    to_port   = number
    sg        = string
  }))
  description = "Rules"
}

variable "users" {
  type        = list(string)
  description = "Usernames"
}