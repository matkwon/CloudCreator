resource "aws_network_interface" "nic" {
  for_each    = { for nic in var.network_interfaces : nic.tags.Name => nic }
  subnet_id   = aws_subnet.subnet[each.value.subnet].id
  private_ips = each.value.private_ips
  #   security_groups = [aws_security_group.web.id]

  #   attachment {
  #     instance = aws_instance.instance[each.value.device].id
  #     # attachment_id     = each.value.device
  #     device_index = 0
  #   }
  tags = each.value.tags
}