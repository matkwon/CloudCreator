variable region {
    type        = string
    description = "AWS region"
}

variable vpc {
    type = object({
        cidr_block = string
        tags       = map(string)
    })
    description = "VPC configuration"
}