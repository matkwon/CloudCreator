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
        cidr_block = string
        tags       = map(string)
    }))
    description = "Subnets configuration"
}

variable "instances" {
    type = list(object({
        ami           = string
        instance_type = string
        tags          = map(string)
    }))
    description = "Instances configuration"
}