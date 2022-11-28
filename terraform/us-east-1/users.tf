resource "aws_iam_user" "user" {
  count         = length(var.users)
  name          = var.users[count.index].name
  force_destroy = true
}

resource "aws_iam_access_key" "user_key" {
  count = length(var.users)
  user  = var.users[count.index].name
}

resource "aws_iam_user_policy" "user_policy" {
  count = length(var.users)
  name  = "${var.users[count.index].name}_policy"
  user  = var.users[count.index].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = var.users[count.index].statements
  })
}