### OpenID provider
# $ terraform import aws_iam_openid_connect_provider.default arn:aws:iam::123456789012:oidc-provider/accounts.google.com
resource "aws_iam_openid_connect_provider" "default" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = []
  tags = []
}

### github action role
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
# $ terraform import aws_iam_role.developer developer_name
resource "aws_iam_role" "github-action-ecr-role" {
  name = "github-action-ecr-role"

  # (1) Allow PowerUser permission for ECR
  # (2) Allow federated role assume with github action
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchGetImage",
          "ecr:GetLifecyclePolicy",
          "ecr:GetLifecyclePolicyPreview",
          "ecr:ListTagsForResource",
          "ecr:DescribeImageScanFindings",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ],
        "Resource": "*"
      },

      {
        "Effect": "Allow",
        "Principal": {
          "Federated": "arn:aws:iam::858070140421:oidc-provider/token.actions.githubusercontent.com"
        },
        "Action": "sts:AssumeRoleWithWebIdentity",
        "Condition": {
          "ForAllValues:StringLike": {
            "token.actions.githubusercontent.com:sub": "repo:kuanpern/aws-test-ga:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}