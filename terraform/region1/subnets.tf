resource "aws_subnet" "subnet" {
  for_each          = { for subnet in var.subnets : subnet.tags.Name => subnet }
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = each.value.cidr_block
  availability_zone = each.value.availability_zone
  tags              = each.value.tags
}