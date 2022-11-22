resource "aws_instance" "instance" {
    for_each      = { for instance in var.instances : instance.tags.Name => instance }
    ami           = each.value.ami
    instance_type = each.value.instance_type
    
    tags = each.value.tags
}