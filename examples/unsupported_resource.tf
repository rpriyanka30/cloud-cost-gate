
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "test_bucket" {
  bucket = "cloud-cost-gate-test-bucket-example"
}
