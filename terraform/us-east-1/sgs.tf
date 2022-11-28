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

  dynamic "ingress" {
    for_each = each.value.ports[*]
    content {
      from_port   = ingress.value.from
      to_port     = ingress.value.to
      protocol    = "tcp"
      cidr_blocks = [aws_vpc.vpc.cidr_block]
    }
  }

  tags = {
    Name = each.value.name
  }
}
