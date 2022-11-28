output "vpc" {
  value = aws_vpc.vpc
}

output "subnets" {
  value = aws_subnet.subnet
}

output "users" {
  value = aws_iam_user.user
}

output "security_groups" {
  value = aws_security_group.sg
}

output "instances" {
  value = aws_instance.instance
}