resource "aws_instance" "instance" {
  for_each      = { for instance in var.instances : instance.tags.Name => instance }
  ami           = "ami-0ee23bfc74a881de5"
  instance_type = each.value.instance_type

  network_interface {
    network_interface_id = aws_network_interface.nic[each.value.nic].id
    device_index         = 0
  }

  tags = each.value.tags
}