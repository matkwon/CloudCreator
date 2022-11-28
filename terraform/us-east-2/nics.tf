resource "aws_network_interface" "nic" {
  for_each    = { for nic in var.network_interfaces : nic.tags.Name => nic }
  subnet_id   = aws_subnet.subnet[each.value.subnet].id
  private_ips = each.value.private_ips
  security_groups = each.value.security_groups
  tags = each.value.tags
}