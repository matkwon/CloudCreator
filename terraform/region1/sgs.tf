resource "aws_security_group_rule" "rule" {
  for_each          = { for rule in var.rules : "${rule.sg}_${rule.from_port}_${rule.to_port}" => rule }
  type              = "ingress"
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = "tcp"
  cidr_blocks       = [aws_vpc.vpc.cidr_block]
  security_group_id = aws_security_group.sg[each.value.sg].id
}

resource "aws_security_group" "sg" {
  for_each    = { for sg in var.security_groups : sg.name => sg }
  name        = each.value.name
  vpc_id      = aws_vpc.vpc.id
  description = each.value.description

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = each.value.name
  }
}
